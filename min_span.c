
__declspec(dllexport)
int* min_span(int n_points, int *pointvals) {
    if (n_points < 2) {
        return 0;
    }

    int *edges = malloc(sizeof(int) * (n_points - 1) * 2);
    int *groups = malloc(sizeof(int) * n_points);

    for (int i = 0; i < n_points; i++) {
        groups[i] = i;
    }

    // There should be len(points) - 1 edges in a min spanning tree
    // If len(points) < 2, there cannot be any edges
    for (int e = 0; e < n_points - 1; e++) {
        int min_edge_len = -1;
        int min_edge_1 = 0;
        int min_edge_2 = 0;
        for (int i = 0; i < n_points * 2; i += 2) {
            for (int j = i; j < n_points * 2; j += 2) {
                // a^2 + b^2 = c^2
                int delta_x =  (pointvals[i] - pointvals[j]);
                int delta_y = (pointvals[i + 1] - pointvals[j + 1]);
                int dist2 = delta_x * delta_x + delta_y * delta_y;
                if ((min_edge_len == -1 || dist2 < min_edge_len) &&
                    groups[i/2] != groups[j/2])
                {
                    min_edge_len = dist2;
                    min_edge_1 = i / 2;
                    min_edge_2 = j / 2;
                }
            }
        }
        edges[e * 2] = min_edge_1;
        edges[e * 2 + 1] = min_edge_2;
        int group1 = groups[min_edge_1];
        int group2 = groups[min_edge_2];
        for (int i = 0; i < n_points; i ++) {
            if (groups[i] == group2) {
                groups[i] = group1;
            }
        }
    }
    free(groups);
    return edges;
}
