# DataMiningShoppingInterface

### Interactive Supermarket Simulation with Association Rule Mining

#### Author Information

- **Names**: Nicholas Wasserman,
- **Student ID**: Nicholas Wasserman: 6300806
- **Course**: CAI 4002 - Artificial Intelligence
- **Semester**: Fall 2025

#### System Overview

[2-3 sentences describing what your application does]

#### Technical Stack

- **Language**: [Python 3.x / JavaScript / Java]
- **Key Libraries**: [List main dependencies]
- **UI Framework**: [If applicable]

#### Installation

##### Prerequisites

- [e.g., Python 3.8+, Node.js 14+, Java 11+]
- [Other requirements]

##### Setup

```bash
# Clone or extract project
cd [project-directory]

# Install dependencies
[command to install dependencies]

# Run application
[command to start application]
```

#### Usage

##### 1. Load Data

- **Manual Entry**: Click items to create transactions
- **Import CSV**: Use "Import" button to load `sample_transactions.csv`

##### 2. Preprocess Data

- Click "Run Preprocessing"
- Review cleaning report (empty transactions, duplicates, etc.)

##### 3. Run Mining

- Set minimum support and confidence thresholds
- Click "Analyze" to execute all three algorithms
- Wait for completion (~1-3 seconds)

##### 4. Query Results

- Select product from dropdown
- View associated items and recommendation strength
- Optional: View technical details (raw rules, performance metrics)

#### Algorithm Implementation

##### Apriori

[2-3 sentences on your implementation approach]

- Data structure: [e.g., dictionary of itemsets]
- Candidate generation: [breadth-first, level-wise]
- Pruning strategy: [minimum support]

##### Eclat

[2-3 sentences on your implementation approach]

- Data structure: [e.g., TID-set representation]
- Search strategy: [depth-first]
- Intersection method: [set operations]

##### CLOSET

[2-3 sentences on your implementation approach]

- Data structure: [e.g., FP-tree / prefix tree]
- Mining approach: [closed itemsets only]
- Closure checking: [method used]

#### Performance Results

Tested on provided dataset (80-100 transactions after cleaning):

| Algorithm | Runtime (ms) | Rules Generated | Max Memory Usage |
| --------- | ------------ | --------------- | ---------------- |
| Apriori   | [112-111]    | [11]            | [71 mb]          |
| Eclat     | [34-35]      | [11 ]           | [71 mb]          |

**Parameters**: min_support = 0.2, min_confidence = 0.5

**Analysis**: [1-2 sentences explaining performance differences]

#### Project Structure

```
project-root/
├── src/
│   ├── algorithms/
│   │   ├── apriori.[py/js/java]
│   │   ├── eclat.[py/js/java]
│   │   └── closet.[py/js/java]
│   ├── preprocessing/
│   │   └── cleaner.[py/js/java]
│   ├── ui/
│   │   └── [interface files]
│   └── main.[py/js/java]
├── data/
│   ├── sample_transactions.csv
│   └── products.csv
├── README.md
├── REPORT.pdf
└── [requirements.txt / package.json / pom.xml]
```

#### Data Preprocessing

Issues handled:

- Empty transactions: [count] removed
- Single-item transactions: [count] removed
- Duplicate items: [count] instances cleaned
- Case inconsistencies: [count] standardized
- Invalid items: [count] removed
- Extra whitespace: trimmed from all items

#### Testing

Verified functionality:

- [✓] CSV import and parsing
- [✓] All preprocessing operations
- [✓] Three algorithm implementations
- [✓] Interactive query system
- [✓] Performance measurement

Test cases:

- [Describe 2-3 key test scenarios]

#### Known Limitations

[List any known issues or constraints, if applicable]

#### AI Tool Usage

ChatGPT Was used for a few things. It was used to write boiler plate UI code. ChatGPT was also used to describe type difference conversion bugs, aswell as how to time the function and
how to measure memory used.

#### References

- Course lecture materials
- Pandas Documentation: https://pandas.pydata.org/docs/user_guide/index.html
- Itertools Documentation: https://docs.python.org/3/library/itertools.html
- Time Documentation: https://docs.python.org/3/library/time.html#module-time
- ECLAT specifications : https://www.youtube.com/watch?v=P5LH5HCrhMU
