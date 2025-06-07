import pandas as pd
import numpy as np
from ortools.linear_solver import pywraplp
import time

def solve_missionary_allocation():
    print("Loading data...")
    # Load the data
    df = pd.read_csv('ALL_DATA.csv')
    
    # Calculate the reach of each missionary
    MISSIONARY_REACH = 10000
    
    # Create a unique identifier for each district (combining state and district)
    df['State_District'] = df['State'] + '_' + df['District']
    
    #Get Unreached population
    df['Unreached Population'] = df['Population'] - df['Christian'].fillna(0)

    # Get unique state-district combinations
    districts = df['State_District'].unique()
    print(f"Number of districts: {len(districts)}")
    
    # Get unique people groups
    people_groups = df['People Group'].unique()
    print(f"Number of people groups: {len(people_groups)}")
    
    # Calculate the total population for each people group
    people_group_totals = df.groupby('People Group')['Population'].sum()
    
    # Calculate the total unreached population for each people group
    christian_people_group_totals = pd.to_numeric(df['Christian'], errors='coerce').fillna(0).groupby(df['People Group']).sum()

    # Print some data summary to help diagnose issues
    print(f"Total population: {df['Population'].sum()}")
    print(f"Sample people group populations: {people_group_totals.head()}")
    
    # Store district details for output
    district_details = {}
    for district in districts:
        state, dist_name = district.split('_', 1)
        district_details[district] = {
            'State': state,
            'District': dist_name
        }
        
        # Add population data for each district
        district_df = df[df['State_District'] == district]
        district_details[district]['Population'] = district_df['Population'].sum()
    
    # Calculate the fraction of each people group in each district
    district_group_fractions = {}
    for district in districts:
        district_df = df[df['State_District'] == district]
        total_district_pop = district_df['Population'].sum()
        
        if total_district_pop > 0:  # Avoid division by zero
            for _, row in district_df.iterrows():
                people_group = row['People Group']
                district_group_fractions[(district, people_group)] = row['Unreached Population'] / total_district_pop
        else:
            for _, row in district_df.iterrows():
                people_group = row['People Group']
                district_group_fractions[(district, people_group)] = 0
    
    print("Setting up the solver...")
    # Try different solvers if one fails
    solver = None
    # Try SCIP first (preferred for integer programming)
    solver = pywraplp.Solver.CreateSolver('SCIP')
    
    if not solver:
        print("SCIP solver not available, trying CBC...")
        solver = pywraplp.Solver.CreateSolver('CBC')
    
    if not solver:
        print("CBC solver not available, trying BOP...")
        solver = pywraplp.Solver.CreateSolver('BOP')
    
    if not solver:
        raise Exception("No MIP solver available. Please install or enable CBC, SCIP, or BOP.")
    
    # Set solver time limit to avoid hanging (30 minutes)
    solver.SetTimeLimit(1800000)  # milliseconds
    
    print("Creating variables...")
    # Create variables: number of missionaries for each district (integer variables)
    missionaries = {}
    for district in districts:
        missionaries[district] = solver.IntVar(0, 10000, f'missionaries_{district}')  # Set a reasonable upper bound
    
    print("Setting up constraints...")
    # Calculate the reach for each people group based on missionary allocation
    reach_per_group = {}
    for people_group in people_groups:
        reach_per_group[people_group] = solver.NumVar(0, solver.infinity(), f'reach_{people_group}')
        reach_constraint = solver.Constraint(0, 0)
        reach_constraint.SetCoefficient(reach_per_group[people_group], 1)
        
        for district in districts:
            if (district, people_group) in district_group_fractions and district_group_fractions[(district, people_group)] > 0:
                # The reach is proportional to the fraction of the people group in the district
                reach_factor = MISSIONARY_REACH * district_group_fractions[(district, people_group)]
                reach_constraint.SetCoefficient(missionaries[district], -reach_factor)
    
    # Constraint: at least 10% of each people group's population must be reached
    for people_group in people_groups:
        if people_group_totals[people_group] > 0:  # Avoid constraints for groups with zero population
            min_reach = 0.1 * people_group_totals[people_group] - christian_people_group_totals[people_group]
            solver.Add(reach_per_group[people_group] >= min_reach)
    
    print("Setting up objective function...")
    # Objective: minimize the total number of missionaries
    objective = solver.Objective()
    for district in districts:
        objective.SetCoefficient(missionaries[district], 1)
    objective.SetMinimization()
    
    print("Solving the problem...")
    start_time = time.time()
    status = solver.Solve()
    solve_time = time.time() - start_time
    print(f"Solve completed in {solve_time:.2f} seconds with status: {status}")
    
    # Process the results
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f'{"Optimal" if status == pywraplp.Solver.OPTIMAL else "Feasible"} solution found')
        total_missionaries = 0
        
        results = []
        for district in districts:
            missionary_count = int(missionaries[district].solution_value())
            if missionary_count > 0:
                state = district_details[district]['State']
                dist_name = district_details[district]['District']
                pop = district_details[district]['Population']
                
                results.append({
                    'State': state,
                    'District': dist_name,
                    'Population': pop,
                    'Missionaries': missionary_count,
                    'Reach_Capacity': missionary_count * MISSIONARY_REACH,
                    'Coverage_Ratio': min(1.0, (missionary_count * MISSIONARY_REACH) / max(1, pop))
                })
                total_missionaries += missionary_count
        
        results_df = pd.DataFrame(results)
        print(f"Total missionaries needed: {total_missionaries}")
        
        # Sort by state and district for better readability
        results_df = results_df.sort_values(['State', 'District'])
        
        # Add columns useful for mapping visualization
        results_df['MissionariesPerCapita'] = results_df['Missionaries'] / results_df['Population'].replace(0, 1)
        results_df['ReachRatio'] = results_df['Reach_Capacity'] / results_df['Population'].replace(0, 1)
        
        # Round floating point values for cleaner output
        for col in ['Coverage_Ratio', 'MissionariesPerCapita', 'ReachRatio']:
            results_df[col] = results_df[col].round(4)
        
        # Save results to CSV
        results_df.to_csv('missionary_allocation_results_unreached_new.csv', index=False)
        
        # Create a separate CSV with coverage per people group
        group_coverage = []
        for people_group in people_groups:
            if people_group_totals[people_group] > 0:
                actual_reach = reach_per_group[people_group].solution_value()
                coverage_percentage = (actual_reach / people_group_totals[people_group]) * 100
                group_coverage.append({
                    'People_Group': people_group,
                    'Total_Population': people_group_totals[people_group],
                    'Reached_Population': actual_reach,
                    'Coverage_Percentage': coverage_percentage
                })
                print(f"{people_group}: {coverage_percentage:.2f}% coverage")
        
        # Save people group coverage to CSV
        pd.DataFrame(group_coverage).to_csv('people_group_coverage_unreached_new.csv', index=False)
        
        return results_df
    else:
        print('No optimal solution found. Status code:', status)
        print('Possible reasons:')
        print('1. The problem may be infeasible - the constraints cannot be satisfied')
        print('2. The solver may have reached the time limit before finding a solution')
        print('3. There might be numerical issues with the problem formulation')
        
        # Try a relaxed version to diagnose issues
        print("\nAttempting to solve a relaxed version (non-integer) to diagnose issues...")
        relaxed_solver = pywraplp.Solver.CreateSolver('GLOP')
        
        # Re-create the model with continuous variables
        relaxed_missionaries = {}
        for district in districts:
            relaxed_missionaries[district] = relaxed_solver.NumVar(0, relaxed_solver.infinity(), f'missionaries_{district}')
        
        # Rebuild the reach calculation
        relaxed_reach = {}
        for people_group in people_groups:
            relaxed_reach[people_group] = 0
            for district in districts:
                if (district, people_group) in district_group_fractions and district_group_fractions[(district, people_group)] > 0:
                    relaxed_reach[people_group] += relaxed_missionaries[district] * MISSIONARY_REACH * district_group_fractions[(district, people_group)]
        
        # Add the 10% coverage constraint
        for people_group in people_groups:
            if people_group_totals[people_group] > 0:
                relaxed_solver.Add(relaxed_reach[people_group] >= 0.1 * people_group_totals[people_group])
        
        # Set objective
        relaxed_objective = relaxed_solver.Objective()
        for district in districts:
            relaxed_objective.SetCoefficient(relaxed_missionaries[district], 1)
        relaxed_objective.SetMinimization()
        
        # Solve relaxed problem
        relaxed_status = relaxed_solver.Solve()
        
        if relaxed_status == pywraplp.Solver.OPTIMAL:
            print("Relaxed problem is solvable. The integer constraints are likely causing the issue.")
            print("Consider increasing the time limit or using a different MIP solver.")
        else:
            print("Even the relaxed problem could not be solved. The constraints may be infeasible.")
        
        return None

if __name__ == "__main__":
    results = solve_missionary_allocation()
    if results is not None:
        print("\nMissionary allocation by district:")
        print(results.head())
        print(f"\nTotal districts with missionaries: {len(results)}")
        print(f"Results saved to 'missionary_allocation_results.csv' and 'people_group_coverage.csv'")