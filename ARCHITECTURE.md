# System Architecture

## Architecture Diagram

```mermaid
graph TD
    User((User)) -->|Interacts| Frontend[Frontend Web Interface\n(HTML/JS/CSS)]
    Frontend -->|HTTP Requests| Server[Python HTTP Server\n(server.py)]
    
    subgraph Backend
        Server -->|API Calls| Engine[Support Engine\n(support_engine.py)]
        
        Engine -->|Orchestrates| DS_Layer[Data Structures Layer\n(data_structures.py)]
        
        subgraph Data_Structures [Data Structures]
            direction TB
            Trie[1. Trie\n(Auto-Complete)]
            HashMap[2. HashMap\n(FAQ & Storage)]
            Tree[3. Decision Tree\n(Conversation Flow)]
            Stack[4. Stack\n(Navigation History)]
            UnionFind[5. Union-Find\n(Intent Normalization)]
            Graph[6. Weighted Graph\n(Action Suggestions)]
            LinkedList[7. Linked List\n(Recently Viewed)]
            PQueue[8. Priority Queue\n(Recommendations)]
            Queue[9. Queue\n(Checkout Flow)]
        end
        
        Engine -.->|Uses| Trie
        Engine -.->|Uses| HashMap
        Engine -.->|Uses| Tree
        Engine -.->|Uses| Stack
        Engine -.->|Uses| UnionFind
        Engine -.->|Uses| Graph
        Engine -.->|Uses| LinkedList
        Engine -.->|Uses| PQueue
        Engine -.->|Uses| Queue
    end

    style Frontend fill:#e1f5fe,stroke:#01579b
    style Server fill:#fff9c4,stroke:#fbc02d
    style Engine fill:#e8f5e9,stroke:#2e7d32
    style DS_Layer fill:#f3e5f5,stroke:#7b1fa2
    style Data_Structures fill:#ffffff,stroke:#999
```

## Component Description

1.  **Frontend**: Lightweight HTML interface that communicates with the backend via REST API.
2.  **Server**: A standalone Python HTTP server that routes requests to the engine.
3.  **Support Engine**: The central controller that manages user sessions and coordinates the correct data structure for each request type.
4.  **Data Structures**: The core algorithmic implementations that power specific features.
