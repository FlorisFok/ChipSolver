def hillsolve(max_tries, matrix, all_sets, unconnected_sets, connected_sets):
    hilltries = 0
    while len(unconnected_sets) > 0 and hilltries < max_tries:
        hilltries += 1
        if hilltries == 1:

            old_routes = {}
            for set in all_sets:
                print("FIRST HILLTRY REMEMBERING ROUTES")
                old_routes[set] = set.get_route()

        np.random.shuffle(connected_sets)

        new_connections = []
        broken_sets = []

        for set in unconnected_sets:
            new_connections.append(set)
            # print(f"These are the unconnected sets in try {hilltries}: {set}, and this set is {set.is_it_connected()}")

        sets_to_be_broken = int(len(connected_sets) * 0.2)
        for i in range(sets_to_be_broken):
            connected_sets[i].disconnect()
            new_connections.append(connected_sets[i])
            broken_sets.append(connected_sets[i])
            # print(f"These sets are being broken now in try {hilltries}:  {connected_sets[i]}, this set is {set.is_it_connected()} ")

        new_all_sets, new_connected_sets, new_unconnected_sets = connect(new_connections)

        print(f"After this {int(len(new_unconnected_sets) / len(all_sets) * 100)}% is unconnected")
        if len(new_unconnected_sets) == 0:
            wire_pieces = 0
            for three_dimensions in matrix:
                for two_dimensions in three_dimensions:
                    for point in two_dimensions:
                        if point.get_attribute() == "wire":
                            wire_pieces += 1
            print(f"SOLUTION HAS BEEN FOUND after {hilltries} hillclimbs, IT TOOK {wire_pieces + len(all_sets)} pieces of wire")

            wire_count = 0
            for set in all_sets:
                for point in set.get_route():
                    if point.get_attribute() == "wire":
                        wire_count += 1

            print(f"ALTERNATIVE COUNT, SOLUTION FOUND AFTER {hilltries} hillclimbs, IT TOOK {wire_count + len(all_sets)} pieces of wire")

            return all_sets

        for set in new_all_sets:
            # print(f"These sets are being disconnected now in try {hilltries}:  {set}, this set is {set.is_it_connected()} ")
            set.disconnect()

        for set in all_sets:
            set.set_route(old_routes[set])

        for set in unconnected_sets:
            set.set_route(old_routes[set])
            set.disconnect()

        for set in connected_sets:
            set.set_route(old_routes[set])
            # print(f"These sets are being reconnected now in try {hilltries}:  {set}, this set is {set.is_it_connected()} ")
            set.reconnect()
