#pragma once
#include<bitset>
#include<array>
#include<vector>
#include<unordered_set>
#include<algorithm>
#include<utility>
#include <time.h>

#include "graph.cpp"

const int MAX_VERTEX_SIZE = 960 * 3;
const int MAX_BMPOOL_SIZE = 3*MAX_VERTEX_SIZE;
using mybitset = std::bitset<MAX_VERTEX_SIZE>;
using myarray = std::array<int, MAX_VERTEX_SIZE>;
using myBMPool = std::array<mybitset, MAX_BMPOOL_SIZE>;
using GMatrix = std::vector<mybitset>;

struct Comp{
  bool operator() (const mybitset &b1, const mybitset &b2) const {
    return b1.to_string() < b2.to_string();
  }
};

using prefixStorage = std::unordered_set<mybitset>;
//using prefixStorage = set<mybitset, Comp>;

inline int findFirstBit(const mybitset &b){
  for(int i = 0, end = b.size(); i < end; ++i){
    if(b[i]) return i;
  }
  return -1;
}

time_t starttime;
double limittime;
inline bool timecheck(){
    return (double)(clock() - starttime) / CLOCKS_PER_SEC > limittime;
}

int vertexSeparationBAB(const int n, const GMatrix &G, std::vector<int> &prefix, std::vector<int> &positions, myarray &bestSeq, int level, mybitset &bPrefix, mybitset &bPrefixAndNeighborhood, int &upperBound, int currentCost, std::vector<mybitset> &bmPool, prefixStorage& prefixStorage, const int limit){
  if(level == n){
    if(currentCost < upperBound){
      for(int i = 0; i < n; ++i) bestSeq[i] = prefix[i];
    }
    return currentCost;
  }
  if(timecheck()) return n;

  int delta_i, v;
  std::vector<std::pair<int,int>> delta;
  int locLevel = level;

  mybitset locBPrefix = bmPool[3*level];
  mybitset locBPrefixAndNeighborhood = bmPool[3*level+1];
  mybitset bTmp = bmPool[3*level+2];

  locBPrefix = bPrefix;
  locBPrefixAndNeighborhood = bPrefixAndNeighborhood;

  // Greedy Step
  int select = 0;
  int i = locLevel;
  int j;
  while(i < n){
    j = prefix[i];
    if(G[j] == (G[j] & locBPrefixAndNeighborhood)){
      locBPrefixAndNeighborhood.set(j);
      select = 1;
    }else if(locBPrefixAndNeighborhood[j] && !locBPrefix[j]){
      bTmp = (G[j] & ~locBPrefixAndNeighborhood);
      if(bTmp.count() == 1){
        //v = bmPool[3*level+2].find_first();
        v = findFirstBit(bTmp);
        locBPrefixAndNeighborhood.set(v);
        select = 1;
      }
    }

    if(select){
      //swap
      if(i != locLevel){
        int pos = i;
        std::swap(positions[prefix[pos]], positions[prefix[locLevel]]);
        std::swap(prefix[pos], prefix[locLevel]);
      }
      ++locLevel;
      locBPrefix.set(j);
      select = 0;
      i = locLevel;
    }else i += 1;
  }

  if(locLevel == n){
    if(currentCost < upperBound){
      for(int i = 0; i < n; ++i) bestSeq[i] = prefix[i];
    }
    return currentCost;
  }

  mybitset frozenPrefix;
  for(int i = 0; i < locLevel; ++i) frozenPrefix.set(prefix[i]);

  if(prefixStorage.count(frozenPrefix)) return upperBound;

  for(int i = locLevel; i < n; ++i){
    j = prefix[i];
    bTmp = locBPrefixAndNeighborhood | G[j];
    bTmp = (bTmp & ~locBPrefix);
    bTmp.reset(j);
    delta_i = bTmp.count();
    if(delta_i < upperBound) delta.emplace_back(delta_i, j);
  }

  // cout << 0 << endl;
  // for(auto &[a, b]: delta) cout << "(" << a << ", " << b << "), ";
  // cout << endl;
  std::sort(delta.begin(), delta.end(), [&](const std::pair<int,int> &l, const std::pair<int,int> &r){
    if(l.first != r.first) return l.first < r.first;
    if(locBPrefixAndNeighborhood[l.second] != locBPrefixAndNeighborhood[r.second]) return locBPrefixAndNeighborhood[l.second] > locBPrefixAndNeighborhood[r.second];
    return l.second < r.second;
  });

  // cout << 1 << endl;
  // for(auto &[a, b]: delta) cout << "(" << a << ", " << b << "), ";
  // cout << endl;
  for(int i = 0; i < std::min(limit, (int)delta.size()); ++i){
    delta_i = delta[i].first;
    i = delta[i].second;

    delta_i = std::max(currentCost, delta_i);
    if(delta_i >= upperBound) break;

    bTmp = locBPrefixAndNeighborhood | G[i];
    bTmp.reset(i);
    //swap
    if(positions[i] != locLevel){
      int pos = positions[i];
      std::swap(positions[prefix[pos]], positions[prefix[locLevel]]);
      std::swap(prefix[pos], prefix[locLevel]);
    }
    locBPrefix.set(i);

    int costI = vertexSeparationBAB(n, G, prefix, positions, bestSeq, locLevel+1, locBPrefix, bTmp, upperBound, delta_i, bmPool, prefixStorage, limit);

    locBPrefix.reset(i);
    if(costI < upperBound){
      upperBound = costI;
    }
  }

  if(currentCost < upperBound) prefixStorage.insert(frozenPrefix);
  return upperBound;
}

std::pair<int, myarray> vertexSeparation(const int &n, const GMatrix& G, const int limit){
  std::vector<mybitset> bmPool(3*n);
  int pw = n;

  std::vector<int> prefix(n);
  std::vector<int> positions(n);
  for(int i = 0; i < n; ++i) {
    prefix[i] = i;
    positions[i] = i;
  }

  mybitset bPrefix;
  mybitset bPrefixAndNeighborhood;

  prefixStorage prefixStorage;

  int upperBound = n;
  myarray bestSeq;

  auto t = vertexSeparationBAB(n, G, prefix, positions, bestSeq, 0, bPrefix, bPrefixAndNeighborhood, upperBound, 0, bmPool, prefixStorage, limit);
  //reverse(ALL(bestSeq));
  // printVec(bestSeq);

  return make_pair(t, bestSeq);
}

GMatrix getMatrix(const Graph& g){
    GMatrix res(g.numVertices());
    for(int u = 0; u < g.numVertices(); ++u){
        for(auto &[v, cost]: g.getNeighbors(u)){
            res[u][v] = 1;
        }
    }
    return res;
}

std::vector<int> decompose(const Graph& graph, const double time, const int limit = 1e9){
  starttime = clock();
  limittime = time;

  GMatrix g = getMatrix(graph);

  auto val = vertexSeparation(g.size(), g, limit);

  std::vector<int> res(g.size());
  for(int i = 0; i < g.size(); ++i) res[i] = val.second[i];
  return res;
}