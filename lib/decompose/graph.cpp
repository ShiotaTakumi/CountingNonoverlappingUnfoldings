#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <set>
#include <stack>
#include <queue>
#include <algorithm>

class Graph {
private:
    int const INF = 1 << 20;

    int const n;
    int const m;
    int const l;
    int const s;
    int const t;
    std::vector<std::pair<std::pair<int, int>, int>> const edge;
    std::vector<std::vector<std::pair<int, int>>> graph;
    std::vector<std::vector<int>> dist;
    int onepair;
    int construct;

public:
    Graph(int n, int m, int l, int s, int t, std::vector<std::pair<std::pair<int, int>, int>> edge) 
        : n(n), m(m), l(l), s(s), t(t), edge(edge) {
        graph.resize(n);
        for(auto it = edge.begin(); it != edge.end(); ++it) {
            int u = (*it).first.first;
            int v = (*it).first.second;
            int c = (*it).second;
            graph[u].push_back(std::make_pair(v, c));
            graph[v].push_back(std::make_pair(u, c));
        }
        onepair = !(s == -1 && t == -1);
        construct = false;
    }

    void constructDist() {
        // Floyd-Warshall Algorithm
        dist.assign(n, std::vector<int>(n, INF));
        for(int i = 0; i < m; i++) {
            int u = edge[i].first.first;
            int v = edge[i].first.second;
            int c = edge[i].second;
            dist[u][v] = c;
            dist[v][u] = c;
        }
        for(int i = 0; i < n; i++) dist[i][i] = 0;
        for(int k = 0; k < n; k++) {
            for(int i = 0; i < n; i++) {
                for(int j = 0; j < n; j++) {
                    dist[i][j] = std::min(dist[i][j], dist[i][k] + dist[k][j]);
                }
            }
        }
        construct = true;
    }

    int isOnepair() const {
        return onepair;
    }

    int getDistance(int u, int v) {
        if(construct == false) constructDist();
        return dist[u][v];
    }

    std::pair<std::pair<int, int>, int> getEdge(int e) const {
        int u = edge[e].first.first;
        int v = edge[e].first.second;
        int c = edge[e].second;
        return std::make_pair(std::make_pair(u, v), c);
    }

    int getStart() const {
        return s;
    }

    int getTerminal() const {
        return t;
    }

    int numVertices() const {
        return n;
    }

    int numEdges() const {
        return m;
    }

    int numLength() const {
        return l;
    }

    std::vector<std::pair<int, int>> getNeighbors(int e) const {
        return graph[e];
    }

    void printEdges() const {
        for(auto it = edge.begin(); it != edge.end(); ++it) {
            std::cout << (*it).first.first << ", " << (*it).first.second << std::endl;
        }
    }

    void print() const {
        std::cout << "Vertices: " << numVertices() << std::endl;
        std::cout << "Edges: "    << numEdges() << std::endl;
        std::cout << "Length: "   << numLength() << std::endl;
        std::cout << "Terminal: " << getStart() << ", " << getTerminal() << std::endl;
        std::cout << "Edge List: " << std::endl;
        printEdges();
    }

    /*
    void print() const {
        std::cout << "-------- Graph Output --------" << std::endl;
        std::cout << "Vertices: " << numVertices() << std::endl;
        std::cout << "Edges: "    << numEdges() << std::endl;
        std::cout << "Length: "   << numLength() << std::endl;
        std::cout << "Terminal: " << getStart() << ", " << getTerminal() << std::endl;
        std::cout << "Edge List: " << std::endl;
        for(int i = 0; i < n; i++) {
            std::cout << i + 1 << ": ";
            for(int j = 0; j < graph[i].size(); j++) {
                std::cout << graph[i][j].first << " ";
            }
            std::cout << std::endl;
        }
        std::cout << "------------------------------" << std::endl;
    }
    */

    Graph deleteVertices() {
        if(construct == false) constructDist();
        std::vector<int> validVertices(n, true);
        std::vector<int> numVertices(n);
        for(int k = 0; k < n; k++) {
            if(dist[s][k] + dist[k][t] > l) validVertices[k] = false;
        }

        int numValidVertices = 0;
        int numValidEdges = 0;
        int idx = 0;
        for(int i = 0; i < n; i++) {
            if(validVertices[i]) {
                numValidVertices++;
                numVertices[i] = idx++;
            }
        }

        std::vector<std::pair<std::pair<int, int>, int>> res_edge;
        for(int i = 0; i < m; i++) {
            int u = edge[i].first.first;
            int v = edge[i].first.second;
            int c = edge[i].second;
            if(validVertices[u] && validVertices[v]) {
                std::pair<int, int> e = std::make_pair(numVertices[u], numVertices[v]);
                res_edge.push_back(std::make_pair(e, c));
                numValidEdges++;
            }
        }
        Graph res(numValidVertices, numValidEdges, l, numVertices[s], numVertices[t], res_edge);
        return res;
    }

    Graph deleteLeaves() {
        std::vector<int> validVertices(n, true);
        std::vector<int> numVertices(n);
        std::vector<std::set<std::pair<int, int>>> g(n);
        for(int i = 0; i < m; i++) {
            int u = edge[i].first.first;
            int v = edge[i].first.second;
            int c = edge[i].second;
            g[u].insert(std::make_pair(v, c));
            g[v].insert(std::make_pair(u, c));
        }

        std::stack<int> stk;
        for(int i = 0; i < n; i++) {
            if(i == s) continue;
            if(i == t) continue;
            if(g[i].size() == 1) {
                stk.push(i);
            }
        }

        while(!stk.empty()) {
            int u = stk.top(); stk.pop();
            if(u == s) continue;
            if(u == t) continue;
            if(g[u].size() == 1) {
                int v = (*g[u].begin()).first;
                int c = (*g[u].begin()).second;
                deleteLeaf(g, u, v, c);
                if(g[v].size() == 1) {
                    stk.push(v);
                }
            }
        }

        /*
        for(int step = 0; step < 2000; step++) {
            for(int i = 0; i < n; i++) {
                if(i == s) continue;
                if(i == t) continue;
                if(g[i].size() == 1) {
                    int u = i;
                    int v = (*g[u].begin()).first;
                    int c = (*g[u].begin()).second;
                    deleteLeaf(g, u, v, c);
                }
            }
        }
        
        for(int i = 0; i < n; i++) {
            if(i == s) continue;
            if(i == t) continue;
            if(g[i].size() == 1) {
                int u = i;
                int v = (*g[u].begin()).first;
                int c = (*g[u].begin()).second;
                deleteLeaf(g, u, v, c);
                while(g[v].size() == 1) {
                    if(v == s) break;
                    if(v == t) break;
                    u = v;
                    v = (*g[u].begin()).first;
                    c = (*g[u].begin()).second;
                    deleteLeaf(g, u, v, c);
                }
            }
        }
        */

        for(int i = 0; i < n; i++) {
            if(g[i].size() == 0) validVertices[i] = false;
        }
        int numValidVertices = 0;
        int numValidEdges = 0;
        int idx = 0;
        for(int i = 0; i < n; i++) {
            if(validVertices[i]) {
                numValidVertices++;
                numVertices[i] = idx++;
            }
        }

        std::vector<std::pair<std::pair<int, int>, int>> res_edge;
        for(int u = 0; u < n; u++) {
            for(auto [v, c]: g[u]) {
                if(u < v) {
                    std::pair<int, int> e = std::make_pair(numVertices[u], numVertices[v]);
                    res_edge.push_back(std::make_pair(e, c));
                    numValidEdges++;
                }
            }
        }
        Graph res(numValidVertices, numValidEdges, l, numVertices[s], numVertices[t], res_edge);
        return res;
    }

    void deleteLeaf(std::vector<std::set<std::pair<int, int>>> &g, int u, int v, int c) {
        g[u].erase(std::make_pair(v, c));
        g[v].erase(std::make_pair(u, c));
    }

    Graph deletePaths() {
        std::vector<int> validVertices(n, true);
        std::vector<int> numVertices(n);
        std::vector<std::multiset<std::pair<int, int>>> g(n);
        for(int i = 0; i < m; i++) {
            int u = edge[i].first.first;
            int v = edge[i].first.second;
            int c = edge[i].second;
            g[u].insert(std::make_pair(v, c));
            g[v].insert(std::make_pair(u, c));
        }

        std::stack<int> stk;
        for(int i = 0; i < n; i++) {
            if(i == s) continue;
            if(i == t) continue;
            if(g[i].size() == 2) {
                stk.push(i);
            }
        }
        
        while(!stk.empty()) {
            int u = stk.top(); stk.pop();
            if(u == s) continue;
            if(u == t) continue;
            if(g[u].size() == 2) {
                int v1 = (*g[u].begin()).first;
                int c1 = (*g[u].begin()).second;
                int v2 = (*g[u].rbegin()).first;
                int c2 = (*g[u].rbegin()).second;
                deletePath(g, u, v1, c1, v2, c2);
                if(g[v1].size() == 2) {
                    stk.push(v1);
                }
                if(g[v2].size() == 2) {
                    stk.push(v2);
                }
            }
        }

        /*
        for(int step = 0; step < 2000; step++) {
            for(int i = 0; i < n; i++) {
                if(i == s) continue;
                if(i == t) continue;
                if(g[i].size() == 2) {
                    int u = i;
                    int v1 = (*g[i].begin()).first;
                    int c1 = (*g[i].begin()).second;
                    int v2 = (*g[i].rbegin()).first;
                    int c2 = (*g[i].rbegin()).second;
                    deletePath(g, u, v1, c1, v2, c2);
                }
            }
        }
        */

        for(int i = 0; i < n; i++) {
            if(g[i].size() == 0) validVertices[i] = false;
        }
        int numValidVertices = 0;
        int numValidEdges = 0;
        int idx = 0;
        for(int i = 0; i < n; i++) {
            if(validVertices[i]) {
                numValidVertices++;
                numVertices[i] = idx++;
            }
        }

        std::vector<std::pair<std::pair<int, int>, int>> res_edge;
        for(int u = 0; u < n; u++) {
            for(auto [v, c]: g[u]) {
                if(u < v) {
                    std::pair<int, int> e = std::make_pair(numVertices[u], numVertices[v]);
                    res_edge.push_back(std::make_pair(e, c));
                    numValidEdges++;
                }
            }
        }
        Graph res(numValidVertices, numValidEdges, l, numVertices[s], numVertices[t], res_edge);
        return res;
    }

    void deletePath(std::vector<std::multiset<std::pair<int, int>>> &g, int u, int v1, int c1, int v2, int c2) {
        g[u].erase(g[u].find(std::make_pair(v1, c1)));
        g[v1].erase(g[v1].find(std::make_pair(u, c1)));
        g[v1].insert(std::make_pair(v2, c1 + c2));

        g[u].erase(g[u].find(std::make_pair(v2, c2)));
        g[v2].erase(g[v2].find(std::make_pair(u, c2)));
        g[v2].insert(std::make_pair(v1, c1 + c2));
    }

    Graph duplicate(int start, int terminal) {
        Graph res(n, m, l, start, terminal, edge);
        return res;
    }
};

Graph readGraph() {
    int n, m, l, s, t;
    s = -1;
    t = -1;
    std::vector<std::pair<std::pair<int, int>, int>> edge;
    char buf[1024];
    while(fgets(buf, sizeof(buf), stdin)) {
        if(buf[0] == 'p') {
            sscanf(buf, "p edge %d %d", &n, &m);
        }
        else if(buf[0] == 'e') {
            int u, v;
            sscanf(buf, "e %d %d", &u, &v);
            u--;
            v--;
            std::pair<int, int> e = std::make_pair(u, v);
            edge.push_back(std::make_pair(e, 1));
        }
        else if(buf[0] == 'l') {
            sscanf(buf, "l %d", &l);
        }
        else if(buf[0] == 't') {
            sscanf(buf, "t %d %d", &s, &t);
            s--;
            t--;
        }
        else if(buf[0] == 'c') {
            continue;
        }
    }
    std::sort(edge.begin(), edge.end());
    Graph G(n, m, l, s, t, edge);
    return G;
}

/*
Graph readGraph(file *char) {
    int n, m, l, s, t;
    s = -1;
    t = -1;
    std::vector<std::pair<std::pair<int, int>, int>> edge;
    char buf[1024];
    FILE *fp;
    if((fp = fopen(file, "r")) == NULL) {
        fprintf(stderr, "Error: cannot open file\n");
        exit(1);
    }
    while(fgets(buf, sizeof(buf), fp)) {
        if(buf[0] == 'p') {
            sscanf(buf, "p edge %d %d", &n, &m);
        }
        else if(buf[0] == 'e') {
            int u, v;
            sscanf(buf, "e %d %d", &u, &v);
            u--;
            v--;
            std::pair<int, int> e = std::make_pair(u, v);
            edge.push_back(std::make_pair(e, 1));
        }
        else if(buf[0] == 'l') {
            sscanf(buf, "l %d", &l);
        }
        else if(buf[0] == 't') {
            sscanf(buf, "t %d %d", &s, &t);
            s--;
            t--;
        }
        else if(buf[0] == 'c') {
            continue;
        }
    }
    std::sort(edge.begin(), edge.end());
    Graph G(n, m, l, s, t, edge);
    return G;
}
*/

void writeGraph(Graph G, char *file) {
    int n = G.numVertices();
    int m = G.numEdges();
    int l = G.numLength();
    int s = G.getStart();
    int t = G.getTerminal();
    s++;
    t++;
    FILE *fp = fopen(file, "wt");
    fprintf(fp, "p edge %d %d\n", n, m);
    for(int i = 0; i < m; i++) {
        int u = G.getEdge(i).first.first;
        int v = G.getEdge(i).first.second;
        int w = G.getEdge(i).second;
        u++;
        v++;
        fprintf(fp, "e %d %d\n", u, v);
    }
    fprintf(fp, "l %d\n", l);
    if(G.isOnepair()) fprintf(fp, "t %d %d\n", s, t);
    fclose(fp);
}

void writeWeightedGraph(Graph G, char *file) {
    int n = G.numVertices();
    int m = G.numEdges();
    int l = G.numLength();
    int s = G.getStart();
    int t = G.getTerminal();
    s++;
    t++;
    FILE *fp = fopen(file, "wt");
    fprintf(fp, "p edge %d %d\n", n, m);
    for(int i = 0; i < m; i++) {
        int u = G.getEdge(i).first.first;
        int v = G.getEdge(i).first.second;
        int w = G.getEdge(i).second;
        u++;
        v++;
        fprintf(fp, "e %d %d\n", u, v, w);
    }
    fprintf(fp, "l %d\n", l);
    if(G.isOnepair()) fprintf(fp, "t %d %d\n", s, t);
    fclose(fp);
}

// void writeGraphWithColor(Graph G, char *file, std::vector<int> comp) {
//     int n = G.numVertices();
//     int m = G.numEdges();
//     int l = G.numLength();
//     int s = G.getStart();
//     int t = G.getTerminal();
//     s++;
//     t++;
//     FILE *fp = fopen(file, "wt"), *pp;
//     fprintf(fp, "p edge %d %d\n", n, m);
//     for(int i = 0; i < n; i++) {
//         fprintf(fp, "v %d %d\n", i + 1, comp[i]);
//     }
//     for(int i = 0; i < m; i++) {
//         int u = G.getEdge(i).first.first;
//         int v = G.getEdge(i).first.second;
//         int w = G.getEdge(i).second;
//         u++;
//         v++;
//         fprintf(fp, "e %d %d\n", u, v);
//     }
//     fprintf(fp, "l %d\n", l);
//     if(G.isOnepair()) fprintf(fp, "t %d %d\n", s, t);
//     fclose(fp);

//     /* python script */
//     char proc[1024];
//     sprintf(proc, "python3 instances-draw/draw_color.py %s", file);
//     if((pp = popen(proc, "r")) == NULL) {
//         fprintf(stderr, "Error: popen()\n");
//         return ;
//     }
//     if(pclose(pp) == -1) {
//         fprintf(stderr, "Error: pclose()\n");
//         return ;
//     }
// }
