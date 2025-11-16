# DataMiningShoppingInterface

### Interactive Supermarket Simulation with Association Rule Mining

#### Author Information

- **Names**: Nicholas Wasserman, Jacob Van
- **Student ID**: Nicholas Wasserman: 6300806, Jacob Van: 6414295
- **Course**: CAI 4002 - Artificial Intelligence
- **Semester**: Fall 2025

#### System Overview

#TODO

#### Technical Stack

- **Language**: [Python3.11.9]
- **Key Libraries**: [List main dependencies]
- **UI Framework**: [Tkinter]

#### Installation

#TODO

##### Prerequisites

- [e.g., Python 3.8+, Node.js 14+, Java 11+]
- [Other requirements]

#TODO

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
| Apriori   | [131]        | [11]            | []               |
| Eclat     | [40]         | [11]            | []               |

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
