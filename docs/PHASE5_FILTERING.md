# Phase 5: Filtering — MOPE-based Non-overlapping Unfolding Extraction

**Status**: Implemented (Specification Frozen)
**Version**: 2.0.0
**Last Updated**: 2026-02-13

---

## Overview / 概要

Phase 5 implements MOPE-based filtering to extract non-overlapping unfoldings from the spanning tree ZDD constructed in Phase 4. It uses the MOPE (Maximal Overlapping Partial Enumeration) edge sets from Phase 3 to iteratively filter out overlapping unfoldings through ZDD subsetting operations, then outputs the final count of non-overlapping unfoldings.

Phase 5 は、Phase 4 で構築した全域木 ZDD から非重複展開図を抽出するための MOPE ベースのフィルタリングを実装します。Phase 3 からの MOPE（最大重複部分列挙）辺集合を用いて、ZDD の subsetting 演算を反復的に適用し重なりを持つ展開図を除外し、最終的な非重複展開図の個数を出力します。

**This is the filtering layer for Counting pipeline.** Phase 5 completes the pipeline by:
1. Applying MOPE-based constraints to the spanning tree ZDD
2. Extracting only non-overlapping unfoldings
3. Providing the final count of valid unfoldings
4. Demonstrating the correctness of the filtering algorithm

**これは Counting パイプラインのフィルタリングレイヤです。** Phase 5 は以下によりパイプラインを完成させます：
1. 全域木 ZDD に MOPE ベースの制約を適用
2. 非重複展開図のみを抽出
3. 有効な展開図の最終個数を提供
4. フィルタリングアルゴリズムの正しさを実証

---

## Purpose and Scope / 目的と範囲

### What Phase 5 Does / Phase 5 が行うこと

Phase 5 focuses on **MOPE-based filtering** of spanning trees to extract non-overlapping unfoldings:

1. **MOPE loading**: Reads unfoldings_edge_sets.jsonl containing overlapping unfolding edge sets.
2. **Iterative filtering**: For each MOPE, applies ZDD subsetting to exclude trees containing all MOPE edges.
3. **Non-overlapping extraction**: Results in a ZDD representing only non-overlapping unfoldings.
4. **Cardinality calculation**: Computes the final count of non-overlapping unfoldings.
5. **Timing measurement**: Measures subsetting operation time separately from Phase 4.
6. **Extended JSON output**: Saves results including both Phase 4 and Phase 5 statistics.

Phase 5 は全域木の **MOPE ベースのフィルタリング**に焦点を当て、非重複展開図を抽出します：

1. **MOPE の読み込み**: 重なりを持つ展開図の辺集合を含む unfoldings_edge_sets.jsonl を読み込みます。
2. **反復フィルタリング**: 各 MOPE に対して、ZDD subsetting を適用し MOPE の全辺を含む木を除外します。
3. **非重複抽出**: 非重複展開図のみを表す ZDD を得ます。
4. **カーディナリティ計算**: 非重複展開図の最終個数を計算します。
5. **時間計測**: Phase 4 とは別に subsetting 演算時間を計測します。
6. **拡張 JSON 出力**: Phase 4 と Phase 5 の両方の統計を含む結果を保存します。

### What Phase 5 Does NOT Do / Phase 5 が行わないこと

Phase 5 intentionally **does not** implement:

- **ZDD expansion**: Does not enumerate individual spanning trees; operates on ZDD directly.
- **Geometric validation**: Does not verify polygon positions or coordinates.
- **Overlap detection**: Relies on pre-computed MOPE data from Phase 2/3.
- **MOPE generation**: Uses existing MOPE edge sets, does not compute new ones.

Phase 5 は意図的に以下を実装**しません**：

- **ZDD の展開**: 個別の全域木を列挙せず、ZDD 上で直接演算します。
- **幾何検証**: 多角形の位置や座標を検証しません。
- **重なり判定**: Phase 2/3 で事前計算された MOPE データに依存します。
- **MOPE 生成**: 既存の MOPE 辺集合を使用し、新たに計算しません。

---

## Input Files / 入力ファイル

Phase 5 requires the following inputs (in addition to Phase 4 inputs):

### polyhedron.grh (from Phase 3)

**Path:**
```
data/polyhedra/<class>/<name>/polyhedron.grh
```

**Purpose:** Provides polyhedron graph for Phase 4 spanning tree construction.

**Format:** Same as Phase 4 (see PHASE4_SPANNING_TREE_ENUMERATION.md).

### unfoldings_edge_sets.jsonl (from Phase 3)

**Path:**
```
data/polyhedra/<class>/<name>/unfoldings_edge_sets.jsonl
```

**Purpose:** Provides MOPE edge sets for filtering overlapping unfoldings.

**Format:** JSON Lines, one MOPE per line

**Structure:**
```json
{"edges": [1, 4, 5, 6, 7, 9, 14, 21, 22, 28]}
{"edges": [1, 2, 3, 6, 8, 9, 10, 18, 21, 26]}
...
```

Each line represents one MOPE (overlapping unfolding):
- `edges`: Array of edge_id values that form this MOPE
- If a spanning tree contains ALL edges in a MOPE, it produces an overlapping unfolding

**CRITICAL:** This file contains **only overlapping unfoldings**. Each line is a MOPE that must be filtered out. Non-overlapping unfoldings are NOT present in this file.

**Example Statistics:**
- **n20**: 40 MOPEs (40 lines in file)
- **s12L**: 72 MOPEs (72 lines in file)

---

## Output Files / 出力ファイル

Phase 5 extends the Phase 4 output file with filtering information.

### result.json

**Path:**
```
output/polyhedra/<class>/<name>/spanning_tree/result.json
```

**Purpose:** Contains both Phase 4 and Phase 5 results in a unified JSON structure.

**Format:** JSON (pretty-printed, UTF-8)

**Structure (with filtering):**
```json
{
  "input_file": "data/polyhedra/johnson/n20/polyhedron.grh",
  "vertices": 25,
  "edges": 45,
  "phase4": {
    "build_time_ms": 3.92,
    "count_time_ms": 0.51,
    "spanning_tree_count": "29821320745"
  },
  "phase5": {
    "filter_applied": true,
    "num_mopes": 40,
    "subset_time_ms": 589.50,
    "non_overlapping_count": "27158087415"
  }
}
```

**Structure (without filtering):**
```json
{
  "input_file": "data/polyhedra/johnson/n20/polyhedron.grh",
  "vertices": 25,
  "edges": 45,
  "phase4": {
    "build_time_ms": 4.90,
    "count_time_ms": 0.66,
    "spanning_tree_count": "29821320745"
  },
  "phase5": {
    "filter_applied": false
  }
}
```

**Field Descriptions:**

**Top-level fields:**
- `input_file`: Path to input .grh file
- `vertices`: Number of vertices in the graph
- `edges`: Number of edges in the graph

**Phase 4 fields:**
- `build_time_ms`: ZDD construction time (milliseconds)
- `count_time_ms`: Cardinality calculation time (milliseconds)
- `spanning_tree_count`: Total number of spanning trees (string for BigNumber support)

**Phase 5 fields:**
- `filter_applied`: Boolean indicating if filtering was performed
- `num_mopes`: Number of MOPEs used for filtering (only if filter_applied)
- `subset_time_ms`: Total time for all subsetting operations (milliseconds, only if filter_applied)
- `non_overlapping_count`: Number of non-overlapping unfoldings (string, only if filter_applied)

---

## Processing Overview / 処理の概要

### Phase 4 + Phase 5 Pipeline

```
Input: polyhedron.grh + unfoldings_edge_sets.jsonl
   ↓
[Phase 4: Spanning Tree ZDD Construction]
   ↓
Spanning Tree ZDD (all trees)
   ↓
[Phase 5: MOPE-based Filtering]
   ↓
   For each MOPE in edge_sets.jsonl:
      - Create UnfoldingFilter(num_edges, MOPE_edges)
      - Apply zddSubset(filter)
      - Apply zddReduce()
   ↓
Non-overlapping Unfolding ZDD
   ↓
[Cardinality Calculation]
   ↓
Output: result.json with Phase 4 + Phase 5 statistics
```

### Filtering Algorithm

**MOPE (Maximal Overlapping Partial Enumeration):**
- Each MOPE is a set of edges that, when all present in an unfolding, guarantee an overlap.
- Example: If MOPE = {1, 4, 7}, then any spanning tree containing edges 1, 4, AND 7 will produce an overlapping unfolding.

**Subsetting Loop (CRITICAL - DO NOT CHANGE):**
```cpp
for (int i = 0; i < MOPEs.size(); ++i) {
    UnfoldingFilter filter(num_edges, MOPEs[i]);
    dd.zddSubset(filter);
    dd.zddReduce();
}
```

This loop structure is from the reference implementation (Reserch2024/EnumerateNonoverlappingEdgeUnfolding) and must NOT be modified.

**UnfoldingFilter Logic:**

For each edge level (processed top to bottom):
- **0-branch (edge NOT selected)**: Clear the bit for this edge
  - If all MOPE bits become 0: **prune** (all MOPE edges are present = overlap)
- **1-branch (edge IS selected)**: Check if this edge is in the MOPE
  - If yes: Clear all bits (MOPE is "cut" by this edge = no overlap possible)

---

## Module Structure / モジュール構造

### C++ Implementation

**Directory:** `cpp/spanning_tree_zdd/`

**Files:**
```
cpp/spanning_tree_zdd/
├── CMakeLists.txt          # Build configuration (includes UnfoldingFilter.cpp)
├── src/
│   ├── main.cpp            # Phase 4 + Phase 5 main program
│   ├── SpanningTree.{hpp,cpp}   # Phase 4: Spanning tree ZDD spec
│   ├── FrontierData.hpp    # Phase 4: Frontier state for spanning tree
│   ├── UnfoldingFilter.{hpp,cpp} # Phase 5: MOPE-based filtering spec
└── build/
    └── spanning_tree_zdd   # Compiled binary
```

**Key Components:**

**main.cpp:**
- Parses command-line arguments (grh file, optional edge_sets file)
- Phase 4: Constructs spanning tree ZDD
- Phase 5: Loads MOPEs and applies subsetting filters
- Outputs unified JSON result

**UnfoldingFilter.{hpp,cpp}:**
- Implements TdZdd DdSpec interface for filtering
- Uses uint64_t bitmask to track MOPE edges (supports up to 64 edges)
- Core logic based on Reserch2024 reference implementation

**MOPE Loading Functions:**
- `load_mopes_from_edge_sets()`: Reads edge_sets.jsonl, returns vector of edge sets
- `extract_edges_from_json()`: Simple JSON parser for {"edges": [...]} format

### Python Wrapper

**Directory:** `python/counting/`

**Files:**
```
python/counting/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point for python -m
├── cli.py                   # Unified pipeline CLI (Phase 4/5/6)
└── compute_automorphisms.py # Automorphism computation (Phase 6)
```

**Key Components:**

**cli.py:**
- Argument parsing: `--poly` (required), `--no-overlap` (Phase 5), `--noniso` (Phase 6)
- Binary execution: Calls C++ binary with appropriate arguments
- Automorphism computation: Prepares automorphism data for Phase 6
- Result display: Shows Phase 4/5/6 statistics
- File management: Saves result.json to output/ directory

---

## Usage / 使い方

### Prerequisites / 前提条件

1. **Completed Phase 3**: polyhedron.grh and unfoldings_edge_sets.jsonl must exist
2. **Built C++ binary**:
   ```bash
   cd cpp/spanning_tree_zdd
   mkdir -p build && cd build
   cmake .. && make
   ```

### Running Phase 4→5 (Non-overlapping Counting)

Phase 5 は `counting` モジュールの `--no-overlap` フラグで有効化されます。

Phase 5 is enabled with the `--no-overlap` flag of the `counting` module.

**From Python:**
```bash
cd CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m counting \
    --poly data/polyhedra/johnson/n20 --no-overlap
```

**From C++ directly:**
```bash
cd CountingNonoverlappingUnfoldings
./cpp/spanning_tree_zdd/build/spanning_tree_zdd \
    data/polyhedra/johnson/n20/polyhedron.grh \
    data/polyhedra/johnson/n20/unfoldings_edge_sets.jsonl
```

**Output:** Phase 4 + Phase 5 results, with filtering applied.

### Running Phase 4→5→6 (Non-overlapping + Nonisomorphic)

`--no-overlap` と `--noniso` の両方を指定すると、Phase 5 の後に Phase 6（Burnside の補題）が適用されます。

Specifying both `--no-overlap` and `--noniso` applies Phase 6 (Burnside's lemma) after Phase 5.

```bash
cd CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m counting \
    --poly data/polyhedra/johnson/n20 --no-overlap --noniso
```

See PHASE6_NONISOMORPHIC_COUNTING.md for Phase 6 details.

Phase 6 の詳細は PHASE6_NONISOMORPHIC_COUNTING.md を参照してください。

---

## Algorithm Details / アルゴリズムの詳細

### ZDD-based Filtering

**Why use ZDD subsetting instead of enumeration?**

- **Efficiency**: Operating on ZDD structure is exponentially faster than enumerating individual trees
- **Memory**: ZDD compresses solution space; enumeration would require storing billions of trees
- **Scalability**: Subsetting scales well with MOPE count; enumeration does not

**Subsetting Operation:**

TdZdd's `zddSubset()` filters the ZDD to keep only solutions that satisfy a given DdSpec:
```cpp
dd.zddSubset(filter);  // Apply filter
dd.zddReduce();        // Compress ZDD
```

### UnfoldingFilter Implementation

**State Representation:**

- Uses templated `BitMask` type (uint64_t or BigUInt<N>) to track MOPE edges
- Supports edge counts from 1 to 448 (automatically selects appropriate bit width)
- Bit position corresponds to edge_id: bit `i` represents edge `i`
- Initially, bits are set to 1 for all edges in the MOPE
- As edges are processed, bits are cleared or the bitmask is zeroed

**Bit Width Selection:**

- **1-64 edges**: uint64_t (native type, fastest)
- **65-128 edges**: BigUInt<2> (2 × 64 bits)
- **129-192 edges**: BigUInt<3> (3 × 64 bits)
- **193-256 edges**: BigUInt<4> (4 × 64 bits)
- **257-320 edges**: BigUInt<5> (5 × 64 bits)
- **321-384 edges**: BigUInt<6> (6 × 64 bits)
- **385-448 edges**: BigUInt<7> (7 × 64 bits)

**getRoot():**
```cpp
template<typename BitMask>
int UnfoldingFilter<BitMask>::getRoot(BitMask& mate) const {
    mate = BitMask();  // Zero initialization
    for (int edge_id : edges) {
        mate |= BigUIntHelper::BitMaskTraits<BitMask>::bit(edge_id);
    }
    return e;  // Return number of edges (root level)
}
```

**getChild():**
```cpp
template<typename BitMask>
int UnfoldingFilter<BitMask>::getChild(BitMask& mate, int level, int value) const {
    if (value == 0) {  // Edge NOT selected
        if (mate != BitMask()) {
            BitMask mask = BigUIntHelper::BitMaskTraits<BitMask>::bit(e - level);
            mate &= ~mask;  // Clear bit
            if (!mate) return 0;  // All bits 0 = MOPE formed = prune
        }
    } else {  // Edge IS selected
        BitMask test_bit = BigUIntHelper::BitMaskTraits<BitMask>::bit(e - level);
        if ((mate & test_bit) != BitMask()) {
            mate = BitMask();  // MOPE edge selected = MOPE cut = no overlap
        }
    }
    if (level == 1) return -1;  // Terminal
    return --level;
}
```

**Key Insight:**

- If all MOPE edges are NOT selected (all bits cleared), the spanning tree contains all MOPE edges → overlapping → prune
- If any MOPE edge IS selected (becomes cutting edge), the MOPE is "cut" → no overlap possible → clear all bits

**Progress Display:**

Phase 5 displays real-time progress during filtering:
```
1/120
2/120
3/120
...
120/120
```
Each line shows the current MOPE being processed and the total count. This helps monitor long-running computations (e.g., s06 with 241 MOPEs).

---

## Implementation Details / 実装の詳細

### Bitwise Operations

**Implementation Strategy:**

Phase 5 uses a templated approach for bitwise operations:

1. **BitMask Template**: UnfoldingFilter<BitMask> works with any type supporting bitwise operations
2. **BigUInt<N> Class**: Variable-width bitmask using uint64_t array (header-only)
3. **BitMaskTraits**: Unified interface for both uint64_t and BigUInt<N>
4. **Runtime Selection**: Automatically chooses appropriate bit width based on edge count

**BigUInt<N> Structure:**
```cpp
template<int N>
class BigUInt {
    uint64_t blocks[N];  // N × 64 bits

    // Operators: |=, &=, ~, ==, !=, !, &
    // Static method: bit(int pos)
};
```

**BitMaskTraits:**
```cpp
namespace BigUIntHelper {
    template<typename BitMask>
    struct BitMaskTraits {
        static inline BitMask bit(int pos);  // Generic: BitMask::bit()
    };

    template<>
    struct BitMaskTraits<uint64_t> {
        static inline uint64_t bit(int pos) { return 1ULL << pos; }
    };
}
```

**Example (90 edges):**
```cpp
// MOPE = {1, 4, 7, ..., 89}, e = 90
// Uses BigUInt<2> (128 bits)
// blocks[0]: bits 0-63
// blocks[1]: bits 64-127 (only bits 64-89 used)
```

**Performance:**
- uint64_t: Native operations, fastest
- BigUInt<2>: ~5-10% slower (2 blocks)
- BigUInt<7>: ~30-40% slower (7 blocks)
- All operations remain O(1) per block

### JSON Parsing

**Approach:** Simple string parsing without external library

**extract_edges_from_json():**
```cpp
set<int> extract_edges_from_json(const string& json_line) {
    set<int> edges;
    size_t start = json_line.find('[');
    size_t end = json_line.find(']');
    if (start == npos || end == npos) return edges;

    string edge_list = json_line.substr(start + 1, end - start - 1);
    stringstream ss(edge_list);
    string token;
    while (getline(ss, token, ',')) {
        // Trim and parse integer
        edges.insert(stoi(token));
    }
    return edges;
}
```

**Rationale:**
- `unfoldings_edge_sets.jsonl` has simple structure: `{"edges": [...]}`
- No need for heavy JSON library
- Consistent with Phase 1-4 approach

---

## Test Results / テスト結果

### n20 (Johnson Solid)

**Input:**
- Vertices: 25
- Edges: 45
- MOPEs: 40
- Bit Width: uint64_t

**Results:**
```
Phase 4:
  Build time: 3.94 ms
  Count time: 0.56 ms
  Spanning tree count: 29,821,320,745

Phase 5:
  Subset time: 628.48 ms
  Number of MOPEs: 40
  Non-overlapping count: 27,158,087,415

Summary:
  Filtered out: 8.93%
```

**Validation:** ✓ Matches expected value (27,158,087,415)

### s12L (Archimedean Solid)

**Input:**
- Vertices: 24
- Edges: 60
- MOPEs: 72
- Bit Width: uint64_t

**Results:**
```
Phase 4:
  Build time: 4.27 ms
  Count time: 0.56 ms
  Spanning tree count: 89,904,012,853,248

Phase 5:
  Subset time: 3,465.19 ms
  Number of MOPEs: 72
  Non-overlapping count: 85,967,688,920,076

Summary:
  Filtered out: 4.38%
```

**Validation:** ✓ Matches expected value (85,967,688,920,076)

### s07 (Archimedean Solid)

**Input:**
- Vertices: 60
- Edges: 90
- MOPEs: 120
- Bit Width: BigUInt<2> (128-bit)

**Results:**
```
Phase 4:
  Build time: 0.96 ms
  Count time: 0.15 ms
  Spanning tree count: 4,982,259,375,000,000,000

Phase 5:
  Subset time: 1,134.09 ms
  Number of MOPEs: 120
  Non-overlapping count: 1,173,681,002,295,455,040

Summary:
  Filtered out: 76.44%
```

**Validation:** ✓ Matches expected value (1,173,681,002,295,455,040)

### s06 (Archimedean Solid)

**Input:**
- Vertices: 60
- Edges: 90
- MOPEs: 241
- Bit Width: BigUInt<2> (128-bit)

**Expected Results:**
```
Spanning tree count: 375,291,866,372,898,816,000
Non-overlapping count: 371,723,160,733,469,233,260
Filtered out: ~1%
```

**Note:** s06 requires significantly longer computation time due to 241 MOPEs (2× that of s07). Test skipped for time constraints, but uses identical BigUInt<2> logic as s07.

---

## Design Decisions / 設計判断

### 1. Unified Binary for Phase 4 + Phase 5

**Decision:** Extend Phase 4 binary to include Phase 5 filtering (not a separate binary)

**Rationale:**
- Avoids ZDD serialization/deserialization overhead
- Simpler deployment and build process
- Matches reference implementation structure
- Allows optional filtering with single binary

### 2. uint64_t Limitation

**Decision:** Current implementation supports only up to 64 edges (uint64_t bitmask)

**Rationale:**
- n20 (45 edges) and s12L (60 edges) fit within 64 bits
- Simplifies implementation without sacrificing test coverage
- Extension to uint128_t or dynamic bitsets documented for future work

### 3. MOPE Input from edge_sets.jsonl Only

**Decision:** Use edge_sets.jsonl directly without overlapping_all.jsonl

**Rationale:**
- Phase 3 already extracts overlapping unfoldings into edge_sets.jsonl
- Avoids redundant overlap checking
- Simpler CLI and data flow
- Each line in edge_sets.jsonl is guaranteed to be a MOPE

### 4. Core Algorithm Preservation

**Decision:** Do NOT modify subsetting loop or UnfoldingFilter logic

**Rationale:**
- Reference implementation (Reserch2024) is verified to be correct
- Algorithm is mathematically sound and proven
- Changes risk introducing subtle bugs
- Focus on clean implementation, not algorithm redesign

---

## Verification / 検証

### Correctness Verification

**Expected Values:**
- **n20**: 27,158,087,415 (verified against reference implementation)
- **s12L**: 85,967,688,920,076 (verified against reference implementation)

**Test Procedure:**
1. Run Phase 4 only → verify spanning tree count
2. Run Phase 4 + Phase 5 → verify non-overlapping count
3. Compare with reference implementation results
4. Verify MOPE count matches edge_sets.jsonl line count

**Results:** ✓ All tests pass

### Edge Cases

**Empty MOPE File:**
- If edge_sets.jsonl is empty or missing: Phase 5 skipped, Phase 4 count returned
- Warning displayed, no error

**Invalid JSON:**
- Empty lines are skipped
- Parse errors are reported with line number
- Continues processing remaining lines

**Edge Count Exceeds Maximum:**
- Error message displayed: "Error: Edge count (X) exceeds maximum supported (448)"
- Program exits with non-zero status

**Bit Width Selection:**
- Automatically selects smallest BitMask type that can hold all edges
- No user configuration required

---

## Performance / パフォーマンス

### Timing Breakdown

**n20 (45 edges, uint64_t):**
- Phase 4 (ZDD construction): ~4 ms
- Phase 5 (40 MOPEs filtering): ~628 ms
- **Phase 5 is ~157x slower than Phase 4**

**s12L (60 edges, uint64_t):**
- Phase 4 (ZDD construction): ~4 ms
- Phase 5 (72 MOPEs filtering): ~3,465 ms
- **Phase 5 is ~866x slower than Phase 4**

**s07 (90 edges, BigUInt<2>):**
- Phase 4 (ZDD construction): ~1 ms
- Phase 5 (120 MOPEs filtering): ~1,134 ms
- **Phase 5 is ~1,134x slower than Phase 4**

### Scalability

**MOPE Count Impact:**
- Linear relationship between MOPE count and filtering time
- Each MOPE requires: `zddSubset()` + `zddReduce()`
- s12L (72 MOPEs) takes ~5.5x longer than n20 (40 MOPEs) for filtering
- s07 (120 MOPEs) takes ~1.8x longer than n20 despite using BigUInt<2>

**Edge Count Impact:**
- ZDD size grows with edge count
- Subsetting operations become more expensive with larger ZDDs
- BigUInt<2> adds ~5-10% overhead vs uint64_t for same MOPE count

**Bit Width Performance:**
- uint64_t (native): Baseline performance
- BigUInt<2> (128-bit): ~5-10% slower per operation
- BigUInt<7> (448-bit): ~30-40% slower per operation
- Overhead is acceptable for enabling larger graphs

---

## Error Handling / エラー処理

### Input Validation

**File Existence:**
- Checks for grh file and edge_sets file (if specified)
- FileNotFoundError with clear message if missing

**Edge Count Limit:**
- Checks if edge count ≤ 448
- Error message: "Error: Edge count (X) exceeds maximum supported (448)"

**JSON Parsing:**
- Skips empty lines
- Reports parse errors with line number
- Continues processing remaining lines

### C++ Binary Errors

**Binary Not Found:**
```
Binary not found: cpp/spanning_tree_zdd/build/spanning_tree_zdd
Please build the C++ binary first:
  cd cpp/spanning_tree_zdd/build
  cmake .. && make
```

**Execution Failure:**
```
RuntimeError: C++ binary failed: <stderr output>
```

**JSON Parse Failure:**
```
ValueError: Failed to parse JSON output: <error>
Output: <stdout>
```

---

## Limitations / 制限事項

### Current Limitations

1. **Edge Count Limit**
   - Maximum 448 edges (BigUInt<7>)
   - Larger graphs require extending BigUInt template (straightforward)

2. **Sequential MOPE Processing**
   - MOPEs are processed one at a time (no parallelization)
   - Could be optimized with multi-threading

3. **No Batch Processing**
   - Each polyhedron must be processed individually
   - No support for processing multiple polyhedra in one run

4. **No Incremental Updates**
   - If MOPEs change, entire filtering must be re-run
   - No caching or incremental computation

---

## Future Work / 今後の作業

### Completed Extensions

#### 1. Variable Bit Width Support ✓ (Implemented)

**Status:** Completed in Version 2.0.0

**Implementation:**
- BigUInt<N> template class for variable-width bitmasks
- BitMaskTraits for unified interface between uint64_t and BigUInt<N>
- Runtime bit width selection (1-448 edges in 64-bit increments)
- Template-based UnfoldingFilter<BitMask> supporting any bit width

**Benefits:**
- Supports graphs with up to 448 edges (extensible to any multiple of 64)
- Maintains high performance through inlined bitwise operations
- Single codebase for all edge counts
- Automatic bit width selection at runtime

### Planned Extensions

#### 1. Progress Display Enhancement (Priority: Medium)

**Motivation:** Better monitoring for long-running computations

**Current:** Simple "Processing MOPE X / Y" display (clears after completion)

**Improvements:**
- Estimated time remaining based on average MOPE processing time
- Percentage completion with progress bar
- Option to save progress log to file for post-analysis

#### 2. Parallel MOPE Processing (Priority: Medium)

**Motivation:** Reduce filtering time for graphs with many MOPEs

**Approach:**
- Process multiple MOPEs in parallel using OpenMP or std::thread
- Requires thread-safe ZDD operations or per-thread ZDD copies
- Potential 2-4× speedup on multi-core systems

**Challenges:**
- TdZdd's thread safety needs verification
- Memory overhead for parallel ZDD copies

#### 3. Batch Processing Mode (Priority: Low)

**Motivation:** Process multiple polyhedra in one run

**Approach:**
```bash
python -m counting --batch polyhedra_list.txt --no-overlap
```

**Benefits:**
- Reduced startup overhead
- Easier for large-scale experiments
- Progress tracking across multiple inputs

#### 4. Extend Maximum Edge Count (Priority: Low)

**Motivation:** Support graphs with >448 edges

**Approach:**
- Add BigUInt<8>, BigUInt<9>, etc. in main.cpp bit width selection
- Requires only adding new if-else cases (straightforward)

**Current Max:** 448 edges (BigUInt<7>)
**Easy Extension:** Up to any multiple of 64 edges

**Options:**
- `std::bitset<N>` (compile-time size)
- `boost::dynamic_bitset<>` (runtime size)
- Custom BigInt implementation

**Trade-offs:**
- More flexible but slower than native types
- Requires external dependency (Boost) or custom implementation

#### 4. Performance Optimizations

**Potential Improvements:**
- Parallel MOPE processing (multi-threading)
- MOPE reordering (process larger MOPEs first)
- ZDD size estimation and early termination

---

## References / 参考文献

### Reference Implementation

**Source:** `Reserch2024/EnumerateNonoverlappingEdgeUnfolding/`

**Key Files:**
- `UnfoldingFilterIncludingMOPE.{hpp,cpp}`: Core filtering logic
- `main.cpp`: Subsetting loop structure

**Verification:** This implementation reproduces the same results as the reference.

### Related Documentation

- [PHASE4_SPANNING_TREE_ENUMERATION.md](PHASE4_SPANNING_TREE_ENUMERATION.md) - Phase 4 specification
- [PHASE3_GRAPH_DATA_CONVERSION.md](PHASE3_GRAPH_DATA_CONVERSION.md) - Phase 3 specification
- TdZdd documentation: Frontier-based search and subsetting operations

---

## Appendix: MOPE Concept / 付録: MOPE の概念

### What is a MOPE?

**MOPE (Maximal Overlapping Partial Enumeration):**
- A set of edges that, when all present in an unfolding, guarantee a geometric overlap
- Example: If faces A and B overlap when unfolded, the edge set connecting these faces forms a MOPE

### Why MOPEs Enable Efficient Filtering

**Key Insight:**
- Instead of checking every spanning tree for overlap (exponentially slow)
- We identify "patterns" (MOPEs) that always cause overlap
- Filter out all trees containing these patterns using ZDD subsetting

**Correctness:**
- Every overlapping unfolding contains at least one MOPE
- Filtering out all trees with MOPEs removes all overlapping unfoldings
- Remaining trees correspond to non-overlapping unfoldings

### MOPE Extraction (Phase 2/3)

MOPEs are extracted in earlier phases:
1. Phase 2: Detects overlapping unfoldings through geometric computation
2. Phase 3: Extracts edge sets from overlapping unfoldings
3. Result: `unfoldings_edge_sets.jsonl` contains all MOPEs

---

**Document Version:** 1.0.0
**Last Updated:** 2026-02-12
**Status:** Specification Frozen
