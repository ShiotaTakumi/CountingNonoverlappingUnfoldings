#pragma once

#include <iostream>
#include <fstream>
#include <vector>
#include <set>
#include <map>
#include <algorithm>

#include "graph.cpp"

std::vector<std::pair<int, int>> convertEdgePermutation(Graph &G, std::vector<int> &perm) {
    int n = G.numVertices();
    int m = G.numEdges();
    /* [Bug]
    std::set<std::pair<int, int>> edge;
    for(int i = 0; i < m; i++) {
        int u = G.getEdge(i).first.first;
        int v = G.getEdge(i).first.second;
        if(v < u) std::swap(u, v);
        edge.insert(std::make_pair(u, v));
    }
    std::vector<std::pair<int, int>> res;
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < i; j++) {
            int u = perm[i];
            int v = perm[j];
            if(v < u) std::swap(u, v);
            if(edge.count(std::make_pair(u, v))) {
                res.push_back(std::make_pair(u, v));
            }
        }
    }
    return res;
    */
    std::map<std::pair<int, int>, int> edge;
    for(int i = 0; i < m; i++) {
        int u = G.getEdge(i).first.first;
        int v = G.getEdge(i).first.second;
        if(v < u) std::swap(u, v);
        edge[std::make_pair(u, v)] += 1;
    }
    std::vector<std::pair<int, int>> res;
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < i; j++) {
            int u = perm[i];
            int v = perm[j];
            if(v < u) std::swap(u, v);
            if(edge.count(std::make_pair(u, v))) {
                for(int k = 0; k < edge[std::make_pair(u, v)]; k++) {
                    res.push_back(std::make_pair(u, v));
                }
            }
        }
    }
    return res;

    /* [debug]
    for(int i = 0; i < res.size(); i++) {
        std::cerr << res[i].first << " " << res[i].second << std::endl;
    }
    */
}

std::vector<int> convertEdgePermutation_weighted(Graph &G, std::vector<int> &perm) {
    int n = G.numVertices();
    int m = G.numEdges();
    std::map<std::pair<int, int>, std::vector<int>> edge;
    for(int i = 0; i < m; i++) {
        int u = G.getEdge(i).first.first;
        int v = G.getEdge(i).first.second;
        int c = G.getEdge(i).second;
        if(v < u) std::swap(u, v);
        edge[std::make_pair(u, v)].push_back(c);
    }
    std::vector<int> res;
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < i; j++) {
            int u = perm[i];
            int v = perm[j];
            if(v < u) std::swap(u, v);
            if(edge.count(std::make_pair(u, v))) {
                for(auto c: edge[std::make_pair(u, v)]) {
                    res.push_back(c);
                }
            }
        }
    }
    return res;

    /* [debug]
    for(int i = 0; i < res.size(); i++) {
        std::cerr << res[i].first << " " << res[i].second << std::endl;
    }
    */
}
