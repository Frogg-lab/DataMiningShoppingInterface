# DataMiningShoppingInterface

### Interactive Supermarket Simulation with Association Rule Mining

#### Author Information

- **Names**: Nicholas Wasserman, Jacob Van, Ethan Drouillard
- **Student ID**: Nicholas Wasserman: 6300806, Jacob Van: 6414295, Ethan Drouillard: 6321129
- **Course**: CAI 4002 - Artificial Intelligence
- **Semester**: Fall 2025

#### System Overview

This project simulates a virtual supermarket where users can interactively select products and analyze purchasing behavior. It utilizes association rule mining (Apriori and ECLAT) to uncover product relationships based on customer transactions. The interface supports importing transaction data, preprocessing, and running mining algorithms to generate rules, which are then queried and displayed in an accessible UI.


#### Technical Stack

- **Language**: [Python3.11.9]
- **Key Libraries**: [List main dependencies]
   - pandas
  - memory_profiler
  - itertools (Python standard)
  - csv (Python standard)
  - tkinter (UI framework)
- **UI Framework**: [Tkinter]

#### Installation

This project runs locally using Python and standard libraries.

##### Prerequisites

- Python 3.10 or later
- pip (Python package manager)

##### Setup

# Install dependencies

pip install -r requirements.txt

# Run application
python src/main.py

If requirements.txt is not available, install manually:
pip install pandas memory_profiler

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

The apiori method was implemented by first cycling through all of the items in the dataset and finding the ones with confidence higher than the
minimum confidence threshold. Then, these frequent singular items are put into size 2 itemsets and kept only if they were also frequent. This continues for
size n until all frequent itemsets are found. Once all of the frequent itemsets are found, they are then broken down to figure out all of the possible
association rules which meet a minimum confidence threshold, which are then returned.

- Data structure: [Dictonary of sizes and sets]
- Candidate generation: [breadth-first, level-wise]
- Pruning strategy: [minimum support]

##### Eclat

The eclat algorithm first translates the data into a vertical format. This allows for the only data acess to be the counting and checking of the intersection of the
tids that each item has. Instead of checking the whole dataset, a total is passed and is multiplied by the support threshold to have a minimum amount of instances needed.
This means to check for frequency, you only have to count the tids of an item, and see if it is above or below the minimum amount, this is significantly faster than
checking the entire dataset each time. Set generation also just takes and stores the tids that intersect for all of the items in the set.

- Data structure: [Dictonary with tuple key and tid values]
- Search strategy: [breadth-first]
- Intersection method: [set operations]

#### Performance Results

Tested on provided dataset (80-100 transactions after cleaning):

| Algorithm | Runtime (ms) | Rules Generated | Max Memory Usage |
| --------- | ------------ | --------------- | ---------------- |
| Apriori   | [131]        | [11]            | [58.90 MiB]               |
| Eclat     | [40]         | [11]            | [57.42 MiB]               |

**Parameters**: min_support = 0.2, min_confidence = 0.5

**Analysis**: Runtime was calculated by runnning the program 20 times, and taking the average of the time taken. With the clean data of 88 transactions,
Eclat was over 3 times faster than the apiori algorithm in generating the same rules.

#### Project Structure

```
project-root/
├── src/
│   ├── algorithms/
│   │   ├── apriori.py
│   │   ├── eclat.py
│   │   └── formulas.py
│   ├── preprocessing/
│   │   └── preprocessing.py
│   ├── ui/
│   │   └── [interface files]
│   └── main.py
├── data/
│   ├── sample_transactions.csv
│   └── products.csv
├── README.md
├── REPORT.pdf
└── [requirements.txt / package.json / pom.xml]


#### Data Preprocessing

Issues handled:

- Empty transactions: [5] removed
- Single-item transactions: [5] removed
- Duplicate items: [9] instances cleaned
- Case inconsistencies all standardized
- Invalid items: [2] removed
- Extra whitespace: trimmed from all items

#### Testing

Verified functionality:

- [✓] CSV import and parsing
- [✓] All preprocessing operations
- [✓] Three algorithm implementations
- [✓] Interactive query system
- [✓] Performance measurement

Test cases:

For testing since i couldnt get packages to work I added the preprocessing script also into the algorithms folder ~ Nick

The system was validated using both synthetic and real-world transaction data. Below are key test scenarios that were executed to ensure robustness and correctness:

Test Case 1: CSV Import and Parsing

Input: sample_transactions.csv with varying item formatting and inconsistencies

Expected Outcome: Transactions are parsed into item lists; extra whitespace, casing differences, and duplicates are cleaned

Result: Successful import with standardized and structured transaction records

Test Case 2: Preprocessing Filters

Input: Transactions containing empty rows, invalid items, or single-item entries

Expected Outcome: Empty and single-item transactions are removed; invalid entries are flagged and cleaned

Result: Dataset reduced to valid, clean transactions suitable for mining

Test Case 3: Apriori Algorithm Accuracy

Input: Cleaned dataset with minimum support = 0.2 and confidence = 0.5

Expected Outcome: All valid association rules are generated, with support and confidence thresholds met

Result: 11 rules generated with average runtime of ~130ms

Test Case 4: ECLAT Efficiency

Input: Same cleaned dataset as Apriori test

Expected Outcome: ECLAT generates the same rule set in less time using vertical data format

Result: 11 rules generated with significantly faster runtime (~40ms)

Test Case 5: UI Interaction

Input: Manual transaction creation and dropdown queries

Expected Outcome: Items are interactively added to transactions, and recommendations reflect mined associations

Result: Real-time feedback and responsive results returned from mining layer

#### Known Limitations

None applicable

#### AI Tool Usage

ChatGPT was used to assist with several development tasks throughout the project. Specifically, it helped:

Generate boilerplate code for the Tkinter-based UI layout

Diagnose and resolve type conversion errors during algorithm integration

Implement function timing for performance benchmarking

Integrate memory profiling to track algorithm efficiency

These contributions streamlined development and ensured clarity in debugging and optimization.

#### References

- Course lecture materials
- Pandas Documentation: https://pandas.pydata.org/docs/user_guide/index.html
- Itertools Documentation: https://docs.python.org/3/library/itertools.html
- Time Documentation: https://docs.python.org/3/library/time.html#module-time
- ECLAT specifications : https://www.youtube.com/watch?v=P5LH5HCrhMU
