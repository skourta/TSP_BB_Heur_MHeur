"""Simple travelling salesman problem between cities."""
from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import Parser
import argparse
import time



def create_data_model(instance):
    """Stores the data for the problem."""
    data = {}
    instance = Parser.TSPInstance(instance)
    instance.readData()
    data['distance_matrix'] = instance.data
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def print_solution(manager, routing, solution):
    """Prints solution on console."""

    index = routing.Start(0)
    plan_output = '[ '
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += '{} '.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' ]'
    print(plan_output)
    print('{}'.format(solution.ObjectiveValue()))
    plan_output += 'Route distance: {}miles\n'.format(route_distance)


def main(instance):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(instance)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    start_time = time.time()
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    end_time = time.time()
    # Print solution on console.
    if solution:
        print_solution(manager, routing, solution)
        print(end_time - start_time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("instance")
    args = parser.parse_args()
    main(args.instance)
