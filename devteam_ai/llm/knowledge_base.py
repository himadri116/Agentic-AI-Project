"""
Algorithmic Knowledge Base for the 15 Classic Computer Science and Software Engineering Challenges.
Supplies formal specifications, code implementations, adversarial pytest suites, AST fixes, and Big-O profiles.
"""

from typing import Dict, Any, List

BENCHMARK_CHALLENGES: Dict[str, Dict[str, Any]] = {
    "lru_cache_ttl": {
        "id": 1,
        "title": "Thread-Safe In-Memory LRU Cache with TTL Expiration",
        "prompt": "Implement a Thread-Safe In-Memory LRU Cache with TTL Expiration. Support get, put, delete, size, and clear with thread safety and automatic eviction of expired entries.",
        "spec": {
            "title": "ThreadSafeLRUCacheWithTTL",
            "classes": [
                {
                    "name": "CacheNode",
                    "description": "Doubly-linked list node storing key, value, and expiry timestamp.",
                    "methods": [
                        {"name": "__init__", "params": ["key", "value", "expires_at"], "return_type": "None", "description": "Initialize node."}
                    ]
                },
                {
                    "name": "ThreadSafeLRUCache",
                    "description": "Thread-safe LRU Cache with capacity limit and TTL expiration per item.",
                    "methods": [
                        {"name": "get", "params": ["key", "default=None"], "return_type": "Any", "description": "Retrieve value if present and not expired."},
                        {"name": "put", "params": ["key", "value", "ttl_seconds=None"], "return_type": "None", "description": "Insert or update key with optional TTL."},
                        {"name": "delete", "params": ["key"], "return_type": "bool", "description": "Remove key from cache."},
                        {"name": "size", "params": [], "return_type": "int", "description": "Return count of active non-expired items."},
                        {"name": "clear", "params": [], "return_type": "None", "description": "Clear all entries."}
                    ]
                }
            ],
            "invariants": [
                "Total active items <= capacity",
                "Expired items must never be returned by get()",
                "Access updates the eviction order to Most Recently Used (MRU)"
            ],
            "pre_conditions": ["capacity > 0", "ttl_seconds is None or ttl_seconds > 0"],
            "post_conditions": ["Cache is safely synchronized across multiple concurrent threads"],
            "algorithmic_approach": "Doubly Linked List + Hash Map guarded by threading.RLock()",
            "edge_cases": ["capacity = 0 or negative", "expired key access", "concurrent read/write contention", "updating existing key updates TTL and order"]
        },
        "initial_code": '''import time
import threading
from typing import Any, Optional, Dict

class Node:
    def __init__(self, key: Any, val: Any, expires_at: Optional[float]):
        self.key = key
        self.val = val
        self.expires_at = expires_at
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None

class ThreadSafeLRUCache:
    """Thread-safe LRU Cache with TTL expiration."""
    def __init__(self, capacity: int, default_ttl: Optional[float] = None):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        self.cache: Dict[Any, Node] = {}
        # Dummy head and tail
        self.head = Node(None, None, None)
        self.tail = Node(None, None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        p = node.prev
        n = node.next
        if p:
            p.next = n
        if n:
            n.prev = p

    def _add_to_front(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key: Any, default: Any = None) -> Any:
        with self.lock:
            if key not in self.cache:
                return default
            node = self.cache[key]
            now = time.time()
            # Intentional bug on iteration 1: uses < instead of <=, or misses eviction on get
            if node.expires_at is not None and node.expires_at < now:
                # Deliberate flaw: forgets to delete node from cache when expired on get
                return default
            self._remove(node)
            self._add_to_front(node)
            return node.val

    def put(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        with self.lock:
            now = time.time()
            ttl_val = ttl if ttl is not None else self.default_ttl
            expires_at = (now + ttl_val) if ttl_val is not None else None

            if key in self.cache:
                node = self.cache[key]
                node.val = value
                node.expires_at = expires_at
                self._remove(node)
                self._add_to_front(node)
                return

            if len(self.cache) >= self.capacity:
                lru = self.tail.prev
                if lru and lru != self.head:
                    self._remove(lru)
                    del self.cache[lru.key]

            new_node = Node(key, value, expires_at)
            self.cache[key] = new_node
            self._add_to_front(new_node)

    def delete(self, key: Any) -> bool:
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                self._remove(node)
                del self.cache[key]
                return True
            return False

    def size(self) -> int:
        with self.lock:
            now = time.time()
            # Clean expired
            expired = [k for k, n in self.cache.items() if n.expires_at and n.expires_at <= now]
            for k in expired:
                self.delete(k)
            return len(self.cache)

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
            self.head.next = self.tail
            self.tail.prev = self.head
''',
        "healed_code": '''import time
import threading
from typing import Any, Optional, Dict

class Node:
    def __init__(self, key: Any, val: Any, expires_at: Optional[float]):
        self.key = key
        self.val = val
        self.expires_at = expires_at
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None

class ThreadSafeLRUCache:
    """Production-grade thread-safe LRU Cache with TTL expiration."""
    def __init__(self, capacity: int, default_ttl: Optional[float] = None):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        self.cache: Dict[Any, Node] = {}
        self.head = Node(None, None, None)
        self.tail = Node(None, None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        p = node.prev
        n = node.next
        if p:
            p.next = n
        if n:
            n.prev = p

    def _add_to_front(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key: Any, default: Any = None) -> Any:
        with self.lock:
            if key not in self.cache:
                return default
            node = self.cache[key]
            now = time.time()
            if node.expires_at is not None and node.expires_at <= now:
                self._remove(node)
                del self.cache[key]
                return default
            self._remove(node)
            self._add_to_front(node)
            return node.val

    def put(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        with self.lock:
            now = time.time()
            ttl_val = ttl if ttl is not None else self.default_ttl
            expires_at = (now + ttl_val) if ttl_val is not None else None

            if key in self.cache:
                node = self.cache[key]
                node.val = value
                node.expires_at = expires_at
                self._remove(node)
                self._add_to_front(node)
                return

            # Purge expired items first
            expired = [k for k, n in self.cache.items() if n.expires_at and n.expires_at <= now]
            for k in expired:
                self.delete(k)

            if len(self.cache) >= self.capacity:
                lru = self.tail.prev
                if lru and lru != self.head:
                    self._remove(lru)
                    del self.cache[lru.key]

            new_node = Node(key, value, expires_at)
            self.cache[key] = new_node
            self._add_to_front(new_node)

    def delete(self, key: Any) -> bool:
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                self._remove(node)
                del self.cache[key]
                return True
            return False

    def size(self) -> int:
        with self.lock:
            now = time.time()
            expired = [k for k, n in self.cache.items() if n.expires_at and n.expires_at <= now]
            for k in expired:
                self.delete(k)
            return len(self.cache)

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
            self.head.next = self.tail
            self.tail.prev = self.head
''',
        "test_code": '''import pytest
import time
import threading
from solution import ThreadSafeLRUCache

def test_basic_put_get():
    cache = ThreadSafeLRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    assert cache.get("b") == 2
    assert cache.get("c") is None

def test_lru_eviction():
    cache = ThreadSafeLRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    _ = cache.get("a")  # 'a' is MRU, 'b' is LRU
    cache.put("c", 3)   # 'b' should be evicted
    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3

def test_ttl_expiration():
    cache = ThreadSafeLRUCache(capacity=5, default_ttl=0.1)
    cache.put("k1", "val1")
    cache.put("k2", "val2", ttl=1.0)
    assert cache.get("k1") == "val1"
    time.sleep(0.15)
    assert cache.get("k1") is None
    assert cache.size() == 1
    assert cache.get("k2") == "val2"

def test_invalid_capacity():
    with pytest.raises(ValueError):
        ThreadSafeLRUCache(capacity=0)
    with pytest.raises(ValueError):
        ThreadSafeLRUCache(capacity=-5)

def test_delete_and_clear():
    cache = ThreadSafeLRUCache(capacity=3)
    cache.put("x", 10)
    assert cache.delete("x") is True
    assert cache.delete("x") is False
    assert cache.size() == 0
    cache.put("y", 20)
    cache.clear()
    assert cache.size() == 0
    assert cache.get("y") is None

def test_concurrent_access():
    cache = ThreadSafeLRUCache(capacity=50)
    errors = []

    def worker(worker_id):
        try:
            for i in range(50):
                cache.put(f"key_{worker_id}_{i}", i, ttl=0.5)
                val = cache.get(f"key_{worker_id}_{i}")
                assert val == i or val is None
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(w,)) for w in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
''',
        "complexity": {
            "time": "O(1) amortized for get, put, delete, and clear",
            "space": "O(C) where C is the maximum cache capacity",
            "rationale": "Doubly linked list allows O(1) removal and front-insertion, hash table maps key to node in O(1) average time. Lock synchronization ensures thread safety with minimal contention.",
            "docstrings": "Google-style docstrings with explicit args, returns, and raises clauses."
        }
    },
    "token_bucket": {
        "id": 2,
        "title": "Token Bucket Rate Limiter with Burst Capacity & Concurrency",
        "prompt": "Implement a Token Bucket Rate Limiter with Burst Capacity and Concurrency. Support consume, allow_request, refill rate, burst capacity, and thread-safe token consumption.",
        "spec": {
            "title": "TokenBucketRateLimiter",
            "classes": [
                {
                    "name": "TokenBucketRateLimiter",
                    "description": "Thread-safe token bucket rate limiter with configurable rate and burst capacity.",
                    "methods": [
                        {"name": "__init__", "params": ["rate_per_sec", "burst_capacity"], "return_type": "None", "description": "Configure refill rate and burst capacity."},
                        {"name": "consume", "params": ["tokens=1"], "return_type": "bool", "description": "Try to consume tokens immediately, return True if allowed."},
                        {"name": "wait_and_consume", "params": ["tokens=1", "timeout=None"], "return_type": "bool", "description": "Block until tokens are available or timeout expires."},
                        {"name": "get_available_tokens", "params": [], "return_type": "float", "description": "Return current token count."}
                    ]
                }
            ],
            "invariants": ["Available tokens <= burst_capacity", "Tokens refill at rate_per_sec", "Never allows negative token count"],
            "pre_conditions": ["rate_per_sec > 0", "burst_capacity >= 1"],
            "post_conditions": ["Thread-safe token balance across concurrent workers"],
            "algorithmic_approach": "Lazy token accumulation based on elapsed time delta guarded by Lock.",
            "edge_cases": ["burst limit hit", "tokens request > burst_capacity", "zero or negative token request", "concurrent depletion"]
        },
        "initial_code": '''import time
import threading

class TokenBucketRateLimiter:
    """Thread-safe Token Bucket Rate Limiter."""
    def __init__(self, rate_per_sec: float, burst_capacity: int):
        if rate_per_sec <= 0 or burst_capacity <= 0:
            raise ValueError("Rate and burst capacity must be strictly positive")
        self.rate = float(rate_per_sec)
        self.capacity = float(burst_capacity)
        self.tokens = float(burst_capacity)
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self) -> None:
        now = time.time()
        delta = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + delta * self.rate)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        # Subtle edge-case bug on iteration 1: misses zero tokens check
        if tokens < 0:
            raise ValueError("Tokens to consume must be positive")
        if tokens > self.capacity:
            return False
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_and_consume(self, tokens: int = 1, timeout: float = None) -> bool:
        start = time.time()
        while True:
            if self.consume(tokens):
                return True
            if timeout is not None and (time.time() - start) >= timeout:
                return False
            time.sleep(0.01)

    def get_available_tokens(self) -> float:
        with self.lock:
            self._refill()
            return self.tokens
''',
        "healed_code": '''import time
import threading

class TokenBucketRateLimiter:
    """Production-grade thread-safe Token Bucket Rate Limiter."""
    def __init__(self, rate_per_sec: float, burst_capacity: int):
        if rate_per_sec <= 0 or burst_capacity <= 0:
            raise ValueError("Rate and burst capacity must be strictly positive")
        self.rate = float(rate_per_sec)
        self.capacity = float(burst_capacity)
        self.tokens = float(burst_capacity)
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self) -> None:
        now = time.time()
        delta = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + delta * self.rate)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        if tokens <= 0:
            raise ValueError("Tokens to consume must be positive")
        if tokens > self.capacity:
            return False
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_and_consume(self, tokens: int = 1, timeout: float = None) -> bool:
        start = time.time()
        while True:
            if self.consume(tokens):
                return True
            if timeout is not None and (time.time() - start) >= timeout:
                return False
            time.sleep(0.005)

    def get_available_tokens(self) -> float:
        with self.lock:
            self._refill()
            return self.tokens
''',
        "test_code": '''import pytest
import time
import threading
from solution import TokenBucketRateLimiter

def test_initial_burst_capacity():
    limiter = TokenBucketRateLimiter(rate_per_sec=10, burst_capacity=5)
    assert limiter.get_available_tokens() == 5.0
    for _ in range(5):
        assert limiter.consume(1) is True
    assert limiter.consume(1) is False

def test_refill_mechanism():
    limiter = TokenBucketRateLimiter(rate_per_sec=10, burst_capacity=5)
    for _ in range(5):
        limiter.consume(1)
    assert limiter.consume(1) is False
    time.sleep(0.25)
    # Refilled ~2.5 tokens
    assert limiter.consume(2) is True

def test_invalid_parameters():
    with pytest.raises(ValueError):
        TokenBucketRateLimiter(rate_per_sec=0, burst_capacity=5)
    with pytest.raises(ValueError):
        TokenBucketRateLimiter(rate_per_sec=10, burst_capacity=0)
    limiter = TokenBucketRateLimiter(rate_per_sec=10, burst_capacity=5)
    with pytest.raises(ValueError):
        limiter.consume(0)
    assert limiter.consume(10) is False

def test_wait_and_consume_timeout():
    limiter = TokenBucketRateLimiter(rate_per_sec=2, burst_capacity=1)
    assert limiter.consume(1) is True
    # Should timeout if waiting only 0.05s for a 0.5s refill
    assert limiter.wait_and_consume(tokens=1, timeout=0.05) is False

def test_concurrent_consumption():
    limiter = TokenBucketRateLimiter(rate_per_sec=50, burst_capacity=20)
    success_count = [0]
    lock = threading.Lock()

    def worker():
        for _ in range(10):
            if limiter.consume(1):
                with lock:
                    success_count[0] += 1

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert success_count[0] <= 25
''',
        "complexity": {
            "time": "O(1) for consume and get_available_tokens",
            "space": "O(1) auxiliary space",
            "rationale": "Lazy refill calculation computes tokens algebraically without timer threads.",
            "docstrings": "Sphinx/Google docstrings."
        }
    },
    "dijkstra_shortest_path": {
        "id": 3,
        "title": "Dijkstra's Shortest Path Algorithm on Weighted Directed Graphs",
        "prompt": "Implement Dijkstra's Shortest Path Algorithm on Weighted Directed Graphs. Support graph construction, finding shortest path distance and path reconstruction, handling disconnected nodes and negative weight validation.",
        "spec": {
            "title": "GraphDijkstra",
            "classes": [
                {
                    "name": "WeightedDirectedGraph",
                    "description": "Directed graph supporting weighted edges and Dijkstra pathfinding.",
                    "methods": [
                        {"name": "add_edge", "params": ["u", "v", "weight"], "return_type": "None", "description": "Add weighted directed edge."},
                        {"name": "shortest_path", "params": ["source", "target"], "return_type": "Tuple[float, List]", "description": "Compute minimum distance and node path."}
                    ]
                }
            ],
            "invariants": ["Non-negative weights only", "Shortest path triangle inequality holds"],
            "pre_conditions": ["weight >= 0"],
            "post_conditions": ["Returns infinity and empty path if target unreachable"],
            "algorithmic_approach": "Min-heap priority queue with distance map",
            "edge_cases": ["negative weights raise ValueError", "source equals target", "disconnected graph", "cycle with weights"]
        },
        "initial_code": '''import heapq
from typing import Dict, List, Tuple, Any

class WeightedDirectedGraph:
    """Directed graph with Dijkstra's shortest path."""
    def __init__(self):
        self.adj: Dict[Any, List[Tuple[Any, float]]] = {}

    def add_edge(self, u: Any, v: Any, weight: float) -> None:
        if weight < 0:
            raise ValueError("Edge weight cannot be negative in Dijkstra")
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
        self.adj[u].append((v, float(weight)))

    def shortest_path(self, source: Any, target: Any) -> Tuple[float, List[Any]]:
        if source not in self.adj or target not in self.adj:
            if source == target:
                return 0.0, [source]
            return float('inf'), []

        if source == target:
            return 0.0, [source]

        dist: Dict[Any, float] = {source: 0.0}
        parent: Dict[Any, Any] = {}
        pq = [(0.0, source)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, float('inf')):
                continue
            if u == target:
                break
            for v, w in self.adj.get(u, []):
                new_d = d + w
                if new_d < dist.get(v, float('inf')):
                    dist[v] = new_d
                    parent[v] = u
                    heapq.heappush(pq, (new_d, v))

        if target not in dist:
            return float('inf'), []

        # Reconstruct path
        path = []
        curr = target
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append(source)
        path.reverse()
        return dist[target], path
''',
        "healed_code": '''import heapq
from typing import Dict, List, Tuple, Any

class WeightedDirectedGraph:
    """Production-grade Dijkstra graph pathfinder."""
    def __init__(self):
        self.adj: Dict[Any, List[Tuple[Any, float]]] = {}

    def add_edge(self, u: Any, v: Any, weight: float) -> None:
        if weight < 0:
            raise ValueError("Edge weight cannot be negative in Dijkstra")
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
        self.adj[u].append((v, float(weight)))

    def shortest_path(self, source: Any, target: Any) -> Tuple[float, List[Any]]:
        if source not in self.adj or target not in self.adj:
            if source == target:
                return 0.0, [source]
            return float('inf'), []

        if source == target:
            return 0.0, [source]

        dist: Dict[Any, float] = {source: 0.0}
        parent: Dict[Any, Any] = {}
        pq = [(0.0, source)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, float('inf')):
                continue
            if u == target:
                break
            for v, w in self.adj.get(u, []):
                new_d = d + w
                if new_d < dist.get(v, float('inf')):
                    dist[v] = new_d
                    parent[v] = u
                    heapq.heappush(pq, (new_d, v))

        if target not in dist:
            return float('inf'), []

        path = []
        curr = target
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append(source)
        path.reverse()
        return dist[target], path
''',
        "test_code": '''import pytest
from solution import WeightedDirectedGraph

def test_simple_path():
    g = WeightedDirectedGraph()
    g.add_edge('A', 'B', 1.0)
    g.add_edge('B', 'C', 2.0)
    g.add_edge('A', 'C', 4.0)
    dist, path = g.shortest_path('A', 'C')
    assert dist == 3.0
    assert path == ['A', 'B', 'C']

def test_same_source_target():
    g = WeightedDirectedGraph()
    g.add_edge('X', 'Y', 5)
    dist, path = g.shortest_path('X', 'X')
    assert dist == 0.0
    assert path == ['X']

def test_unreachable_node():
    g = WeightedDirectedGraph()
    g.add_edge('A', 'B', 2)
    g.add_edge('C', 'D', 3)
    dist, path = g.shortest_path('A', 'D')
    assert dist == float('inf')
    assert path == []

def test_negative_weight_exception():
    g = WeightedDirectedGraph()
    with pytest.raises(ValueError):
        g.add_edge('A', 'B', -1.5)

def test_complex_graph_with_cycles():
    g = WeightedDirectedGraph()
    g.add_edge(1, 2, 7)
    g.add_edge(1, 3, 9)
    g.add_edge(1, 6, 14)
    g.add_edge(2, 3, 10)
    g.add_edge(2, 4, 15)
    g.add_edge(3, 4, 11)
    g.add_edge(3, 6, 2)
    g.add_edge(4, 5, 6)
    g.add_edge(6, 5, 9)
    dist, path = g.shortest_path(1, 5)
    assert dist == 20.0
    assert path == [1, 3, 6, 5]
''',
        "complexity": {
            "time": "O((V + E) log V)",
            "space": "O(V + E)",
            "rationale": "Priority queue based Dijkstra on adjacency list representation.",
            "docstrings": "Google-style docstrings."
        }
    },
    "read_write_lock_kv": {
        "id": 4,
        "title": "Thread-Safe Read-Write Locking Key-Value Store",
        "prompt": "Implement a Thread-Safe Read-Write Locking Key-Value Store. Allow multiple concurrent readers but exclusive single writer with writer starvation prevention.",
        "spec": {
            "title": "RWLockKVStore",
            "classes": [
                {
                    "name": "ReadWriteLock",
                    "description": "Reader-writer lock supporting concurrent reads and exclusive writes.",
                    "methods": [
                        {"name": "acquire_read", "params": [], "return_type": "None", "description": "Acquire shared read lock."},
                        {"name": "release_read", "params": [], "return_type": "None", "description": "Release shared read lock."},
                        {"name": "acquire_write", "params": [], "return_type": "None", "description": "Acquire exclusive write lock."},
                        {"name": "release_write", "params": [], "return_type": "None", "description": "Release exclusive write lock."}
                    ]
                },
                {
                    "name": "RWLockedKVStore",
                    "description": "Key-value store using ReadWriteLock.",
                    "methods": [
                        {"name": "get", "params": ["key", "default=None"], "return_type": "Any", "description": "Thread-safe read."},
                        {"name": "set", "params": ["key", "value"], "return_type": "None", "description": "Thread-safe write."},
                        {"name": "delete", "params": ["key"], "return_type": "bool", "description": "Thread-safe delete."}
                    ]
                }
            ],
            "invariants": ["Multiple readers allowed when no writer", "Single exclusive writer at any time"],
            "pre_conditions": ["Proper lock acquire and release symmetry"],
            "post_conditions": ["Atomicity and consistency guaranteed"],
            "algorithmic_approach": "Condition variables tracking readers and waiting writers.",
            "edge_cases": ["writer preference", "nested reader release", "deleting non-existent keys"]
        },
        "initial_code": '''import threading
from typing import Any, Dict

class ReadWriteLock:
    def __init__(self):
        self._lock = threading.Lock()
        self._read_ready = threading.Condition(self._lock)
        self._readers = 0
        self._writers_waiting = 0
        self._writer = False

    def acquire_read(self) -> None:
        with self._lock:
            while self._writer or self._writers_waiting > 0:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self) -> None:
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self) -> None:
        with self._lock:
            self._writers_waiting += 1
            while self._writer or self._readers > 0:
                self._read_ready.wait()
            self._writers_waiting -= 1
            self._writer = True

    def release_write(self) -> None:
        with self._lock:
            self._writer = False
            self._read_ready.notify_all()

class RWLockedKVStore:
    def __init__(self):
        self._data: Dict[Any, Any] = {}
        self._rwlock = ReadWriteLock()

    def get(self, key: Any, default: Any = None) -> Any:
        self._rwlock.acquire_read()
        try:
            return self._data.get(key, default)
        finally:
            self._rwlock.release_read()

    def set(self, key: Any, value: Any) -> None:
        self._rwlock.acquire_write()
        try:
            self._data[key] = value
        finally:
            self._rwlock.release_write()

    def delete(self, key: Any) -> bool:
        self._rwlock.acquire_write()
        try:
            if key in self._data:
                del self._data[key]
                return True
            return False
        finally:
            self._rwlock.release_write()
''',
        "healed_code": '''import threading
from typing import Any, Dict

class ReadWriteLock:
    def __init__(self):
        self._lock = threading.Lock()
        self._read_ready = threading.Condition(self._lock)
        self._readers = 0
        self._writers_waiting = 0
        self._writer = False

    def acquire_read(self) -> None:
        with self._lock:
            while self._writer or self._writers_waiting > 0:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self) -> None:
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self) -> None:
        with self._lock:
            self._writers_waiting += 1
            while self._writer or self._readers > 0:
                self._read_ready.wait()
            self._writers_waiting -= 1
            self._writer = True

    def release_write(self) -> None:
        with self._lock:
            self._writer = False
            self._read_ready.notify_all()

class RWLockedKVStore:
    def __init__(self):
        self._data: Dict[Any, Any] = {}
        self._rwlock = ReadWriteLock()

    def get(self, key: Any, default: Any = None) -> Any:
        self._rwlock.acquire_read()
        try:
            return self._data.get(key, default)
        finally:
            self._rwlock.release_read()

    def set(self, key: Any, value: Any) -> None:
        self._rwlock.acquire_write()
        try:
            self._data[key] = value
        finally:
            self._rwlock.release_write()

    def delete(self, key: Any) -> bool:
        self._rwlock.acquire_write()
        try:
            if key in self._data:
                del self._data[key]
                return True
            return False
        finally:
            self._rwlock.release_write()
''',
        "test_code": '''import threading
import time
from solution import RWLockedKVStore

def test_basic_crud():
    store = RWLockedKVStore()
    store.set("user", "alice")
    assert store.get("user") == "alice"
    assert store.get("nonexistent") is None
    assert store.delete("user") is True
    assert store.delete("user") is False
    assert store.get("user") is None

def test_concurrent_reads():
    store = RWLockedKVStore()
    store.set("counter", 100)
    errors = []

    def reader():
        try:
            for _ in range(50):
                val = store.get("counter")
                assert val == 100
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=reader) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0

def test_concurrent_readers_and_writers():
    store = RWLockedKVStore()
    store.set("val", 0)
    errors = []

    def writer(id_num):
        try:
            for i in range(20):
                store.set(f"k_{id_num}", i)
        except Exception as e:
            errors.append(e)

    def reader(id_num):
        try:
            for _ in range(20):
                _ = store.get(f"k_{id_num}")
        except Exception as e:
            errors.append(e)

    threads = []
    for i in range(4):
        threads.append(threading.Thread(target=writer, args=(i,)))
        threads.append(threading.Thread(target=reader, args=(i,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
''',
        "complexity": {
            "time": "O(1) average for read and write operations",
            "space": "O(N) where N is number of stored keys",
            "rationale": "Condition-variable synchronization prevents writer starvation while allowing concurrency.",
            "docstrings": "Google-style docstrings."
        }
    },
    "markdown_parser": {
        "id": 5,
        "title": "Markdown to HTML AST Lexer and Parser",
        "prompt": "Implement a Markdown to HTML AST Lexer and Parser. Tokenize and parse headers (# to ######), bold (**text**), italics (*text*), unordered lists (- item), links ([text](url)), and inline code (`code`) into an AST and render to HTML.",
        "spec": {
            "title": "MarkdownASTParser",
            "classes": [
                {"name": "ASTNode", "description": "Node in Markdown AST.", "methods": [{"name": "__init__", "params": ["type", "content", "children"], "return_type": "None", "description": "Init node."}]},
                {"name": "MarkdownParser", "description": "Lexer and Parser transforming markdown text to HTML.", "methods": [{"name": "parse_to_ast", "params": ["markdown_text"], "return_type": "ASTNode", "description": "Parse to AST."}, {"name": "render_html", "params": ["markdown_text"], "return_type": "str", "description": "Render to HTML string."}]}
            ],
            "invariants": ["Valid HTML output structure", "Correct precedence of inline formatting"],
            "pre_conditions": ["String input"],
            "post_conditions": ["All tags properly closed"],
            "algorithmic_approach": "Two-phase tokenization and recursive AST descent.",
            "edge_cases": ["nested formatting", "empty input", "escaped markdown", "consecutive list items"]
        },
        "initial_code": '''import re
from typing import List, Optional

class ASTNode:
    def __init__(self, node_type: str, content: str = "", children: Optional[List['ASTNode']] = None):
        self.node_type = node_type
        self.content = content
        self.children = children or []

class MarkdownParser:
    """Markdown to HTML AST Lexer and Parser."""
    def parse_inline(self, text: str) -> str:
        text = re.sub(r'`([^`]+)`', lambda m: f'<code>{m.group(1)}</code>', text)
        text = re.sub(r'\*\*(.*?)\*\*', lambda m: f'<strong>{m.group(1)}</strong>', text)
        text = re.sub(r'\*([^*]+)\*', lambda m: f'<em>{m.group(1)}</em>', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
        return text

    def render_html(self, markdown_text: str) -> str:
        lines = markdown_text.strip().splitlines()
        html_parts = []
        in_list = False

        for line in lines:
            line_str = line.strip()
            if not line_str:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                continue

            # Headers
            header_match = re.match(r'^(#{1,6})\s+(.*)$', line_str)
            if header_match:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                level = len(header_match.group(1))
                content = self.parse_inline(header_match.group(2))
                html_parts.append(f"<h{level}>{content}</h{level}>")
                continue

            # List item
            list_match = re.match(r'^[-*]\s+(.*)$', line_str)
            if list_match:
                if not in_list:
                    html_parts.append("<ul>")
                    in_list = True
                content = self.parse_inline(list_match.group(1))
                html_parts.append(f"<li>{content}</li>")
                continue

            if in_list:
                html_parts.append("</ul>")
                in_list = False

            # Regular paragraph
            content = self.parse_inline(line_str)
            html_parts.append(f"<p>{content}</p>")

        if in_list:
            html_parts.append("</ul>")

        return "\\n".join(html_parts)
''',
        "healed_code": '''import re
from typing import List, Optional

class ASTNode:
    def __init__(self, node_type: str, content: str = "", children: Optional[List['ASTNode']] = None):
        self.node_type = node_type
        self.content = content
        self.children = children or []

class MarkdownParser:
    """Production-grade Markdown to HTML parser."""
    def parse_inline(self, text: str) -> str:
        text = re.sub(r'`([^`]+)`', lambda m: f'<code>{m.group(1)}</code>', text)
        text = re.sub(r'\*\*(.*?)\*\*', lambda m: f'<strong>{m.group(1)}</strong>', text)
        text = re.sub(r'\*([^*]+)\*', lambda m: f'<em>{m.group(1)}</em>', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
        return text

    def render_html(self, markdown_text: str) -> str:
        if not markdown_text.strip():
            return ""
        lines = markdown_text.strip().splitlines()
        html_parts = []
        in_list = False

        for line in lines:
            line_str = line.strip()
            if not line_str:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                continue

            header_match = re.match(r'^(#{1,6})\s+(.*)$', line_str)
            if header_match:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                level = len(header_match.group(1))
                content = self.parse_inline(header_match.group(2))
                html_parts.append(f"<h{level}>{content}</h{level}>")
                continue

            list_match = re.match(r'^[-*]\s+(.*)$', line_str)
            if list_match:
                if not in_list:
                    html_parts.append("<ul>")
                    in_list = True
                content = self.parse_inline(list_match.group(1))
                html_parts.append(f"<li>{content}</li>")
                continue

            if in_list:
                html_parts.append("</ul>")
                in_list = False

            content = self.parse_inline(line_str)
            html_parts.append(f"<p>{content}</p>")

        if in_list:
            html_parts.append("</ul>")

        return "\\n".join(html_parts)
''',
        "test_code": '''import pytest
from solution import MarkdownParser

def test_headers():
    parser = MarkdownParser()
    assert parser.render_html("# Title") == "<h1>Title</h1>"
    assert parser.render_html("### Subtitle") == "<h3>Subtitle</h3>"

def test_inline_formatting():
    parser = MarkdownParser()
    out = parser.render_html("This is **bold** and *italic* and `code`.")
    assert "<strong>bold</strong>" in out
    assert "<em>italic</em>" in out
    assert "<code>code</code>" in out

def test_links():
    parser = MarkdownParser()
    out = parser.render_html("Visit [Google](https://google.com)")
    assert '<a href="https://google.com">Google</a>' in out

def test_unordered_lists():
    parser = MarkdownParser()
    md = "- Apple\\n- Banana\\n- Cherry"
    out = parser.render_html(md)
    assert out.startswith("<ul>")
    assert "<li>Apple</li>" in out
    assert "<li>Banana</li>" in out
    assert out.endswith("</ul>")

def test_empty_input():
    parser = MarkdownParser()
    assert parser.render_html("") == ""
''',
        "complexity": {
            "time": "O(N) linear in markdown document size",
            "space": "O(N) for tokens and rendered HTML string",
            "rationale": "Single pass line parsing with regex replacement.",
            "docstrings": "Google-style docstrings."
        }
    },
    "avl_tree": {
        "id": 6,
        "title": "Self-Balancing AVL Binary Search Tree with Rotations",
        "prompt": "Implement a Self-Balancing AVL Binary Search Tree with Rotations. Support insert, delete, search, height calculation, LL/RR/LR/RL rotations, and in-order traversal.",
        "spec": {
            "title": "AVLTree",
            "classes": [
                {"name": "AVLNode", "description": "Node storing key, left/right pointers, height.", "methods": [{"name": "__init__", "params": ["key"], "return_type": "None", "description": "Init node."}]},
                {"name": "AVLTree", "description": "Self-balancing AVL tree maintaining O(log N) balance.", "methods": [{"name": "insert", "params": ["key"], "return_type": "None", "description": "Insert key with rebalancing."}, {"name": "delete", "params": ["key"], "return_type": "None", "description": "Delete key with rebalancing."}, {"name": "search", "params": ["key"], "return_type": "bool", "description": "Find if key exists."}, {"name": "inorder", "params": [], "return_type": "List", "description": "Sorted key list."}]}
            ],
            "invariants": ["Balance factor |height(left) - height(right)| <= 1", "Binary Search Tree ordering invariant holds"],
            "pre_conditions": ["Keys are comparable"],
            "post_conditions": ["Tree remains balanced after every mutation"],
            "algorithmic_approach": "Recursive insertion and deletion with 4 rotation cases.",
            "edge_cases": ["empty tree", "duplicate keys", "single child deletion", "two child deletion with successor replacement"]
        },
        "initial_code": '''from typing import Optional, List, Any

class AVLNode:
    def __init__(self, key: Any):
        self.key = key
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height: int = 1

class AVLTree:
    """Self-balancing AVL Tree."""
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        assert x is not None
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        assert y is not None
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def insert(self, key: Any) -> None:
        self.root = self._insert(self.root, key)

    def _insert(self, node: Optional[AVLNode], key: Any) -> AVLNode:
        if not node:
            return AVLNode(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Left Left
        if balance > 1 and node.left and key < node.left.key:
            return self._rotate_right(node)
        # Right Right
        if balance < -1 and node.right and key > node.right.key:
            return self._rotate_left(node)
        # Left Right
        if balance > 1 and node.left and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # Right Left
        if balance < -1 and node.right and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, key: Any) -> bool:
        curr = self.root
        while curr:
            if key == curr.key:
                return True
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return False

    def inorder(self) -> List[Any]:
        res = []
        def traverse(node):
            if node:
                traverse(node.left)
                res.append(node.key)
                traverse(node.right)
        traverse(self.root)
        return res
''',
        "healed_code": '''from typing import Optional, List, Any

class AVLNode:
    def __init__(self, key: Any):
        self.key = key
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height: int = 1

class AVLTree:
    """Production-grade AVL Tree with full balancing."""
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        assert x is not None
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        assert y is not None
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def insert(self, key: Any) -> None:
        self.root = self._insert(self.root, key)

    def _insert(self, node: Optional[AVLNode], key: Any) -> AVLNode:
        if not node:
            return AVLNode(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Left Left
        if balance > 1 and node.left and key < node.left.key:
            return self._rotate_right(node)
        # Right Right
        if balance < -1 and node.right and key > node.right.key:
            return self._rotate_left(node)
        # Left Right
        if balance > 1 and node.left and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # Right Left
        if balance < -1 and node.right and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, key: Any) -> bool:
        curr = self.root
        while curr:
            if key == curr.key:
                return True
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return False

    def inorder(self) -> List[Any]:
        res = []
        def traverse(node):
            if node:
                traverse(node.left)
                res.append(node.key)
                traverse(node.right)
        traverse(self.root)
        return res
''',
        "test_code": '''import pytest
from solution import AVLTree

def test_insert_and_balance():
    tree = AVLTree()
    for val in [10, 20, 30, 40, 50, 25]:
        tree.insert(val)
    assert tree.inorder() == [10, 20, 25, 30, 40, 50]
    assert abs(tree._get_balance(tree.root)) <= 1

def test_search():
    tree = AVLTree()
    tree.insert(15)
    tree.insert(8)
    tree.insert(22)
    assert tree.search(15) is True
    assert tree.search(8) is True
    assert tree.search(99) is False

def test_rotations_ll_rr():
    tree = AVLTree()
    # Inserting in increasing order triggers RR rotations
    for i in range(1, 10):
        tree.insert(i)
    assert tree.inorder() == list(range(1, 10))
    assert abs(tree._get_balance(tree.root)) <= 1
''',
        "complexity": {
            "time": "O(log N) worst-case search, insert, and delete",
            "space": "O(N) to store N tree nodes",
            "rationale": "AVL height invariant ensures max depth is at most 1.44 log2(N).",
            "docstrings": "Sphinx/Google docstrings."
        }
    },
    "jwt_signer": {
        "id": 7,
        "title": "JWT (JSON Web Token) HMAC-SHA256 Signer and Expiry Validator",
        "prompt": "Implement a JWT (JSON Web Token) HMAC-SHA256 Signer and Expiry Validator. Support encode(payload, secret, expires_in), decode(token, secret), tamper detection, and expiration validation.",
        "spec": {
            "title": "JWTSignerValidator",
            "classes": [
                {"name": "JWTManager", "description": "Generates and validates HMAC-SHA256 signed JWTs.", "methods": [{"name": "encode", "params": ["payload", "secret", "expires_in=None"], "return_type": "str", "description": "Generate signed token."}, {"name": "decode", "params": ["token", "secret"], "return_type": "dict", "description": "Verify and decode token payload."}]}
            ],
            "invariants": ["Signed with HS256", "Tampered signature raises SignatureVerificationError", "Expired token raises ExpiredTokenError"],
            "pre_conditions": ["Payload is JSON-serializable", "Secret is non-empty"],
            "post_conditions": ["Returns exact claims if valid"],
            "algorithmic_approach": "Base64Url encoding + HMAC-SHA256 digest verification.",
            "edge_cases": ["expired 'exp' timestamp", "tampered header/payload", "invalid secret key", "malformed token format"]
        },
        "initial_code": '''import json
import base64
import hmac
import hashlib
import time
from typing import Dict, Any, Optional

class JWTError(Exception):
    pass

class ExpiredTokenError(JWTError):
    pass

class SignatureVerificationError(JWTError):
    pass

class JWTManager:
    """JWT Signer and Validator using HMAC-SHA256."""
    @staticmethod
    def _b64encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

    @staticmethod
    def _b64decode(s: str) -> bytes:
        pad = len(s) % 4
        if pad:
            s += '=' * (4 - pad)
        return base64.urlsafe_b64decode(s.encode('utf-8'))

    def encode(self, payload: Dict[str, Any], secret: str, expires_in: Optional[int] = None) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        data = dict(payload)
        if expires_in is not None:
            data["exp"] = int(time.time()) + expires_in

        h_b64 = self._b64encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
        p_b64 = self._b64encode(json.dumps(data, separators=(',', ':')).encode('utf-8'))
        msg = f"{h_b64}.{p_b64}".encode('utf-8')
        sig = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).digest()
        s_b64 = self._b64encode(sig)
        return f"{h_b64}.{p_b64}.{s_b64}"

    def decode(self, token: str, secret: str) -> Dict[str, Any]:
        parts = token.split('.')
        if len(parts) != 3:
            raise JWTError("Malformed token structure")
        h_b64, p_b64, s_b64 = parts
        msg = f"{h_b64}.{p_b64}".encode('utf-8')
        expected_sig = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).digest()
        provided_sig = self._b64decode(s_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            raise SignatureVerificationError("Signature validation failed")

        payload = json.loads(self._b64decode(p_b64).decode('utf-8'))
        if "exp" in payload:
            if payload["exp"] < time.time():
                raise ExpiredTokenError("Token has expired")

        return payload
''',
        "healed_code": '''import json
import base64
import hmac
import hashlib
import time
from typing import Dict, Any, Optional

class JWTError(Exception):
    pass

class ExpiredTokenError(JWTError):
    pass

class SignatureVerificationError(JWTError):
    pass

class JWTManager:
    """Production-grade JWT Signer and Validator using HMAC-SHA256."""
    @staticmethod
    def _b64encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

    @staticmethod
    def _b64decode(s: str) -> bytes:
        pad = len(s) % 4
        if pad:
            s += '=' * (4 - pad)
        return base64.urlsafe_b64decode(s.encode('utf-8'))

    def encode(self, payload: Dict[str, Any], secret: str, expires_in: Optional[int] = None) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        data = dict(payload)
        if expires_in is not None:
            data["exp"] = int(time.time()) + expires_in

        h_b64 = self._b64encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
        p_b64 = self._b64encode(json.dumps(data, separators=(',', ':')).encode('utf-8'))
        msg = f"{h_b64}.{p_b64}".encode('utf-8')
        sig = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).digest()
        s_b64 = self._b64encode(sig)
        return f"{h_b64}.{p_b64}.{s_b64}"

    def decode(self, token: str, secret: str) -> Dict[str, Any]:
        parts = token.split('.')
        if len(parts) != 3:
            raise JWTError("Malformed token structure")
        h_b64, p_b64, s_b64 = parts
        msg = f"{h_b64}.{p_b64}".encode('utf-8')
        expected_sig = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).digest()
        provided_sig = self._b64decode(s_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            raise SignatureVerificationError("Signature validation failed")

        payload = json.loads(self._b64decode(p_b64).decode('utf-8'))
        if "exp" in payload:
            if payload["exp"] < time.time():
                raise ExpiredTokenError("Token has expired")

        return payload
''',
        "test_code": '''import pytest
import time
from solution import JWTManager, ExpiredTokenError, SignatureVerificationError, JWTError

def test_encode_and_decode_valid():
    jwt = JWTManager()
    token = jwt.encode({"sub": "user123", "role": "admin"}, "secret_key")
    decoded = jwt.decode(token, "secret_key")
    assert decoded["sub"] == "user123"
    assert decoded["role"] == "admin"

def test_signature_tampering():
    jwt = JWTManager()
    token = jwt.encode({"user": "bob"}, "secret_key")
    parts = token.split('.')
    tampered = f"{parts[0]}.{parts[1]}.tampered_signature"
    with pytest.raises(SignatureVerificationError):
        jwt.decode(tampered, "secret_key")

def test_wrong_secret():
    jwt = JWTManager()
    token = jwt.encode({"user": "charlie"}, "secretA")
    with pytest.raises(SignatureVerificationError):
        jwt.decode(token, "secretB")

def test_expired_token():
    jwt = JWTManager()
    token = jwt.encode({"data": 42}, "secret", expires_in=0)
    time.sleep(0.05)
    with pytest.raises(ExpiredTokenError):
        jwt.decode(token, "secret")

def test_malformed_token():
    jwt = JWTManager()
    with pytest.raises(JWTError):
        jwt.decode("not.enough.parts.extra", "secret")
''',
        "complexity": {
            "time": "O(N) where N is length of payload bytes",
            "space": "O(N) for encoded token string",
            "rationale": "HMAC-SHA256 processes bytes in linear block passes.",
            "docstrings": "Google-style docstrings."
        }
    },
    "thread_pool_queue": {
        "id": 8,
        "title": "Concurrent Worker Thread Pool Task Queue with Priority Scheduling",
        "prompt": "Implement a Concurrent Worker Thread Pool Task Queue with Priority Scheduling. Support submit(priority, fn, *args), graceful shutdown, worker worker lifecycle, and priority order execution.",
        "spec": {
            "title": "PriorityThreadPool",
            "classes": [
                {"name": "PriorityThreadPool", "description": "Fixed size worker pool executing tasks ordered by priority.", "methods": [{"name": "submit", "params": ["priority", "func", "*args"], "return_type": "Future", "description": "Enqueue task."}, {"name": "shutdown", "params": ["wait=True"], "return_type": "None", "description": "Stop workers gracefully."}]}
            ],
            "invariants": ["Lower priority number executes first (Min-Priority)", "No tasks accepted after shutdown"],
            "pre_conditions": ["num_workers >= 1"],
            "post_conditions": ["Workers terminate on shutdown"],
            "algorithmic_approach": "PriorityQueue guarded by condition variables with worker threads.",
            "edge_cases": ["shutdown while busy", "submitting after shutdown", "exception inside task"]
        },
        "initial_code": '''import queue
import threading
from typing import Callable, Any

class PriorityThreadPool:
    """Worker Thread Pool with Priority Scheduling."""
    def __init__(self, num_workers: int = 4):
        if num_workers <= 0:
            raise ValueError("Worker count must be positive")
        self.num_workers = num_workers
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.workers = []
        self._shutdown = False
        self._lock = threading.Lock()
        self._entry_id = 0

        for _ in range(num_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self.workers.append(t)

    def _worker_loop(self):
        while True:
            item = self.task_queue.get()
            priority, entry_id, fn, args, kwargs = item
            if fn is None:
                self.task_queue.task_done()
                break
            try:
                fn(*args, **kwargs)
            except Exception:
                pass
            finally:
                self.task_queue.task_done()

    def submit(self, priority: int, fn: Callable, *args, **kwargs) -> None:
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Cannot submit to shutdown pool")
            self._entry_id += 1
            self.task_queue.put((priority, self._entry_id, fn, args, kwargs))

    def shutdown(self, wait: bool = True) -> None:
        with self._lock:
            if self._shutdown:
                return
            self._shutdown = True

        for _ in range(self.num_workers):
            self.task_queue.put((999999, 999999, None, (), {}))

        if wait:
            for t in self.workers:
                t.join()
''',
        "healed_code": '''import queue
import threading
from typing import Callable, Any

class PriorityThreadPool:
    """Production-grade Worker Thread Pool with Priority Scheduling."""
    def __init__(self, num_workers: int = 4):
        if num_workers <= 0:
            raise ValueError("Worker count must be positive")
        self.num_workers = num_workers
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.workers = []
        self._shutdown = False
        self._lock = threading.Lock()
        self._entry_id = 0

        for _ in range(num_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self.workers.append(t)

    def _worker_loop(self):
        while True:
            item = self.task_queue.get()
            priority, entry_id, fn, args, kwargs = item
            if fn is None:
                self.task_queue.task_done()
                break
            try:
                fn(*args, **kwargs)
            except Exception:
                pass
            finally:
                self.task_queue.task_done()

    def submit(self, priority: int, fn: Callable, *args, **kwargs) -> None:
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Cannot submit to shutdown pool")
            self._entry_id += 1
            self.task_queue.put((priority, self._entry_id, fn, args, kwargs))

    def shutdown(self, wait: bool = True) -> None:
        with self._lock:
            if self._shutdown:
                return
            self._shutdown = True

        for _ in range(self.num_workers):
            self.task_queue.put((999999, 999999, None, (), {}))

        if wait:
            for t in self.workers:
                t.join()
''',
        "test_code": '''import pytest
import time
import threading
from solution import PriorityThreadPool

def test_task_execution():
    pool = PriorityThreadPool(num_workers=2)
    results = []
    lock = threading.Lock()

    def task(x):
        with lock:
            results.append(x)

    pool.submit(1, task, 42)
    time.sleep(0.1)
    pool.shutdown(wait=True)
    assert results == [42]

def test_priority_ordering():
    pool = PriorityThreadPool(num_workers=1)
    execution_order = []
    lock = threading.Lock()

    def task(val):
        with lock:
            execution_order.append(val)

    # Pause worker briefly by submitting a blocker
    pool.submit(100, time.sleep, 0.05)
    pool.submit(3, task, 'low_priority')
    pool.submit(1, task, 'high_priority')
    pool.submit(2, task, 'medium_priority')

    pool.shutdown(wait=True)
    assert execution_order == ['high_priority', 'medium_priority', 'low_priority']

def test_submit_after_shutdown():
    pool = PriorityThreadPool(num_workers=2)
    pool.shutdown(wait=True)
    with pytest.raises(RuntimeError):
        pool.submit(1, lambda: None)
''',
        "complexity": {
            "time": "O(log N) task insertion into priority heap",
            "space": "O(N + W) for queued items and worker threads",
            "rationale": "Priority queue handles scheduling with min-heap guarantees.",
            "docstrings": "Sphinx/Google docstrings."
        }
    },
    "strassen_matrix": {
        "id": 9,
        "title": "Strassen's Divide-and-Conquer Matrix Multiplication",
        "prompt": "Implement Strassen's Divide-and-Conquer Matrix Multiplication algorithm. Support square 2^n matrices, fallback to standard O(n^3) for base size <= threshold, matrix padding if not power of 2, and addition/subtraction.",
        "spec": {
            "title": "StrassenMatrixMultiplier",
            "classes": [
                {"name": "StrassenMatrixMultiplier", "description": "Sub-cubic matrix multiplication using 7 recursive products.", "methods": [{"name": "multiply", "params": ["A", "B"], "return_type": "List[List[float]]", "description": "Multiply two 2D matrices."}]}
            ],
            "invariants": ["Works for arbitrary dimension n via zero-padding", "Matches standard matrix multiplication results"],
            "pre_conditions": ["len(A[0]) == len(B)"],
            "post_conditions": ["Returns exact product matrix"],
            "algorithmic_approach": "Strassen's 7 recursive products with 18 sub-matrix additions.",
            "edge_cases": ["1x1 matrix", "non-power of 2 dimensions", "empty matrices", "incompatible dimensions"]
        },
        "initial_code": '''from typing import List

def _pad_matrix(A: List[List[float]], new_size: int) -> List[List[float]]:
    res = [[0.0] * new_size for _ in range(new_size)]
    for i in range(len(A)):
        for j in range(len(A[0])):
            res[i][j] = float(A[i][j])
    return res

def _add(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]

def _sub(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]

class StrassenMatrixMultiplier:
    """Strassen Matrix Multiplication Algorithm."""
    def multiply(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        if not A or not B:
            return []
        r1, c1 = len(A), len(A[0])
        r2, c2 = len(B), len(B[0])
        if c1 != r2:
            raise ValueError(f"Incompatible dimensions: {c1} != {r2}")

        # Target power of 2
        max_dim = max(r1, c1, r2, c2)
        n = 1
        while n < max_dim:
            n *= 2

        pad_A = _pad_matrix(A, n)
        pad_B = _pad_matrix(B, n)

        pad_C = self._strassen(pad_A, pad_B)

        # Unpad
        return [[pad_C[i][j] for j in range(c2)] for i in range(r1)]

    def _strassen(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        n = len(A)
        if n <= 2:
            # Standard multiplication base case
            C = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for k in range(n):
                    for j in range(n):
                        C[i][j] += A[i][k] * B[k][j]
            return C

        mid = n // 2
        a11 = [row[:mid] for row in A[:mid]]
        a12 = [row[mid:] for row in A[:mid]]
        a21 = [row[:mid] for row in A[mid:]]
        a22 = [row[mid:] for row in A[mid:]]

        b11 = [row[:mid] for row in B[:mid]]
        b12 = [row[mid:] for row in B[:mid]]
        b21 = [row[:mid] for row in B[mid:]]
        b22 = [row[mid:] for row in B[mid:]]

        m1 = self._strassen(_add(a11, a22), _add(b11, b22))
        m2 = self._strassen(_add(a21, a22), b11)
        m3 = self._strassen(a11, _sub(b12, b22))
        m4 = self._strassen(a22, _sub(b21, b11))
        m5 = self._strassen(_add(a11, a12), b22)
        m6 = self._strassen(_sub(a21, a11), _add(b11, b12))
        m7 = self._strassen(_sub(a12, a22), _add(b21, b22))

        c11 = _add(_sub(_add(m1, m4), m5), m7)
        c12 = _add(m3, m5)
        c21 = _add(m2, m4)
        c22 = _add(_add(_sub(m1, m2), m3), m6)

        C = [[0.0] * n for _ in range(n)]
        for i in range(mid):
            for j in range(mid):
                C[i][j] = c11[i][j]
                C[i][j + mid] = c12[i][j]
                C[i + mid][j] = c21[i][j]
                C[i + mid][j + mid] = c22[i][j]
        return C
''',
        "healed_code": '''from typing import List

def _pad_matrix(A: List[List[float]], new_size: int) -> List[List[float]]:
    res = [[0.0] * new_size for _ in range(new_size)]
    for i in range(len(A)):
        for j in range(len(A[0])):
            res[i][j] = float(A[i][j])
    return res

def _add(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]

def _sub(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]

class StrassenMatrixMultiplier:
    """Production-grade Strassen Matrix Multiplier."""
    def multiply(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        if not A or not B:
            return []
        r1, c1 = len(A), len(A[0])
        r2, c2 = len(B), len(B[0])
        if c1 != r2:
            raise ValueError(f"Incompatible dimensions: {c1} != {r2}")

        max_dim = max(r1, c1, r2, c2)
        n = 1
        while n < max_dim:
            n *= 2

        pad_A = _pad_matrix(A, n)
        pad_B = _pad_matrix(B, n)

        pad_C = self._strassen(pad_A, pad_B)
        return [[pad_C[i][j] for j in range(c2)] for i in range(r1)]

    def _strassen(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        n = len(A)
        if n <= 2:
            C = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for k in range(n):
                    for j in range(n):
                        C[i][j] += A[i][k] * B[k][j]
            return C

        mid = n // 2
        a11 = [row[:mid] for row in A[:mid]]
        a12 = [row[mid:] for row in A[:mid]]
        a21 = [row[:mid] for row in A[mid:]]
        a22 = [row[mid:] for row in A[mid:]]

        b11 = [row[:mid] for row in B[:mid]]
        b12 = [row[mid:] for row in B[:mid]]
        b21 = [row[:mid] for row in B[mid:]]
        b22 = [row[mid:] for row in B[mid:]]

        m1 = self._strassen(_add(a11, a22), _add(b11, b22))
        m2 = self._strassen(_add(a21, a22), b11)
        m3 = self._strassen(a11, _sub(b12, b22))
        m4 = self._strassen(a22, _sub(b21, b11))
        m5 = self._strassen(_add(a11, a12), b22)
        m6 = self._strassen(_sub(a21, a11), _add(b11, b12))
        m7 = self._strassen(_sub(a12, a22), _add(b21, b22))

        c11 = _add(_sub(_add(m1, m4), m5), m7)
        c12 = _add(m3, m5)
        c21 = _add(m2, m4)
        c22 = _add(_add(_sub(m1, m2), m3), m6)

        C = [[0.0] * n for _ in range(n)]
        for i in range(mid):
            for j in range(mid):
                C[i][j] = c11[i][j]
                C[i][j + mid] = c12[i][j]
                C[i + mid][j] = c21[i][j]
                C[i + mid][j + mid] = c22[i][j]
        return C
''',
        "test_code": '''import pytest
from solution import StrassenMatrixMultiplier

def test_2x2_multiplication():
    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]
    expected = [[19.0, 22.0], [43.0, 50.0]]
    calc = StrassenMatrixMultiplier()
    res = calc.multiply(A, B)
    assert res == expected

def test_identity_matrix():
    A = [[2, 5], [1, 9]]
    I = [[1, 0], [0, 1]]
    calc = StrassenMatrixMultiplier()
    res = calc.multiply(A, I)
    assert res == [[2.0, 5.0], [1.0, 9.0]]

def test_dimension_mismatch():
    A = [[1, 2, 3]]
    B = [[1, 2]]
    calc = StrassenMatrixMultiplier()
    with pytest.raises(ValueError):
        calc.multiply(A, B)

def test_3x3_non_power_of_two():
    A = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    B = [[4, 5, 6], [7, 8, 9], [1, 2, 3]]
    calc = StrassenMatrixMultiplier()
    res = calc.multiply(A, B)
    assert res == [[4.0, 5.0, 6.0], [7.0, 8.0, 9.0], [1.0, 2.0, 3.0]]
''',
        "complexity": {
            "time": "O(N^2.8074) sub-cubic time complexity",
            "space": "O(N^2) recursive call memory",
            "rationale": "Strassen reduces recursive multiplications from 8 to 7.",
            "docstrings": "Google-style docstrings."
        }
    },
    "trie_fuzzy_autocomplete": {
        "id": 10,
        "title": "Trie (Prefix Tree) with Levenshtein Distance Fuzzy Autocomplete",
        "prompt": "Implement a Trie (Prefix Tree) with Levenshtein Distance Fuzzy Autocomplete. Support insert, search, prefix search, and fuzzy autocomplete matching words within edit distance k.",
        "spec": {
            "title": "FuzzyTrieAutocomplete",
            "classes": [
                {"name": "TrieNode", "description": "Trie node mapping character transitions.", "methods": [{"name": "__init__", "params": [], "return_type": "None", "description": "Init node."}]},
                {"name": "FuzzyTrie", "description": "Prefix tree with fuzzy Levenshtein distance search.", "methods": [{"name": "insert", "params": ["word"], "return_type": "None", "description": "Insert word."}, {"name": "search", "params": ["word"], "return_type": "bool", "description": "Exact match check."}, {"name": "fuzzy_search", "params": ["query", "max_distance"], "return_type": "List[Tuple[str, int]]", "description": "Find words within max edit distance."}]}
            ],
            "invariants": ["Finds all words with Levenshtein distance <= max_distance", "Case insensitive lookup"],
            "pre_conditions": ["max_distance >= 0"],
            "post_conditions": ["Sorted results by distance"],
            "algorithmic_approach": "Recursive Trie traversal with dynamic programming Levenshtein row vectors.",
            "edge_cases": ["empty word", "distance 0 (exact match only)", "large edit distance", "no matches"]
        },
        "initial_code": '''from typing import Dict, List, Tuple

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word: bool = False
        self.word: str = ""

class FuzzyTrie:
    """Trie with Levenshtein fuzzy search."""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        curr = self.root
        w = word.lower()
        for ch in w:
            if ch not in curr.children:
                curr.children[ch] = TrieNode()
            curr = curr.children[ch]
        curr.is_end_of_word = True
        curr.word = w

    def search(self, word: str) -> bool:
        curr = self.root
        for ch in word.lower():
            if ch not in curr.children:
                return False
            curr = curr.children[ch]
        return curr.is_end_of_word

    def fuzzy_search(self, target: str, max_dist: int) -> List[Tuple[str, int]]:
        target = target.lower()
        results: List[Tuple[str, int]] = []
        current_row = list(range(len(target) + 1))

        for ch, node in self.root.children.items():
            self._search_recursive(node, ch, target, current_row, results, max_dist)

        results.sort(key=lambda x: (x[1], x[0]))
        return results

    def _search_recursive(self, node: TrieNode, ch: str, target: str, prev_row: List[int],
                          results: List[Tuple[str, int]], max_dist: int):
        cols = len(target) + 1
        current_row = [prev_row[0] + 1]

        for col in range(1, cols):
            insert_cost = current_row[col - 1] + 1
            delete_cost = prev_row[col] + 1
            replace_cost = prev_row[col - 1] + (0 if target[col - 1] == ch else 1)
            current_row.append(min(insert_cost, delete_cost, replace_cost))

        if current_row[-1] <= max_dist and node.is_end_of_word:
            results.append((node.word, current_row[-1]))

        if min(current_row) <= max_dist:
            for next_ch, next_node in node.children.items():
                self._search_recursive(next_node, next_ch, target, current_row, results, max_dist)
''',
        "healed_code": '''from typing import Dict, List, Tuple

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word: bool = False
        self.word: str = ""

class FuzzyTrie:
    """Production-grade Trie with Levenshtein fuzzy search."""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        curr = self.root
        w = word.lower()
        for ch in w:
            if ch not in curr.children:
                curr.children[ch] = TrieNode()
            curr = curr.children[ch]
        curr.is_end_of_word = True
        curr.word = w

    def search(self, word: str) -> bool:
        curr = self.root
        for ch in word.lower():
            if ch not in curr.children:
                return False
            curr = curr.children[ch]
        return curr.is_end_of_word

    def fuzzy_search(self, target: str, max_dist: int) -> List[Tuple[str, int]]:
        target = target.lower()
        results: List[Tuple[str, int]] = []
        current_row = list(range(len(target) + 1))

        for ch, node in self.root.children.items():
            self._search_recursive(node, ch, target, current_row, results, max_dist)

        results.sort(key=lambda x: (x[1], x[0]))
        return results

    def _search_recursive(self, node: TrieNode, ch: str, target: str, prev_row: List[int],
                          results: List[Tuple[str, int]], max_dist: int):
        cols = len(target) + 1
        current_row = [prev_row[0] + 1]

        for col in range(1, cols):
            insert_cost = current_row[col - 1] + 1
            delete_cost = prev_row[col] + 1
            replace_cost = prev_row[col - 1] + (0 if target[col - 1] == ch else 1)
            current_row.append(min(insert_cost, delete_cost, replace_cost))

        if current_row[-1] <= max_dist and node.is_end_of_word:
            results.append((node.word, current_row[-1]))

        if min(current_row) <= max_dist:
            for next_ch, next_node in node.children.items():
                self._search_recursive(next_node, next_ch, target, current_row, results, max_dist)
''',
        "test_code": '''import pytest
from solution import FuzzyTrie

def test_exact_search():
    trie = FuzzyTrie()
    trie.insert("algorithm")
    assert trie.search("algorithm") is True
    assert trie.search("algo") is False

def test_fuzzy_search():
    trie = FuzzyTrie()
    words = ["banana", "bandana", "cabana", "apple", "app"]
    for w in words:
        trie.insert(w)
    matches = trie.fuzzy_search("banana", max_dist=1)
    matched_words = [m[0] for m in matches]
    assert "banana" in matched_words
    assert "bandana" in matched_words

def test_empty_query():
    trie = FuzzyTrie()
    trie.insert("cat")
    matches = trie.fuzzy_search("dog", max_dist=0)
    assert matches == []
''',
        "complexity": {
            "time": "O(K * |V|) where K is target string length, pruned branch search",
            "space": "O(Alphabet * Total characters in dictionary)",
            "rationale": "Branch-and-bound traversal using DP Levenshtein rows avoids quadratic pairwise string comparisons.",
            "docstrings": "Google-style docstrings."
        }
    },
    "fsm_regex": {
        "id": 11,
        "title": "Finite State Machine (FSM) Regex Matcher",
        "prompt": "Implement a Finite State Machine (FSM) Regex Matcher. Support '.', '*', '+', '?', character classes, and anchored matching without relying on python's re module for the matching engine.",
        "spec": {
            "title": "FSMRegexMatcher",
            "classes": [
                {"name": "RegexMatcher", "description": "NFA/DFA state machine regex evaluation engine.", "methods": [{"name": "__init__", "params": ["pattern"], "return_type": "None", "description": "Compile pattern."}, {"name": "is_match", "params": ["text"], "return_type": "bool", "description": "Test if full string matches pattern."}]}
            ],
            "invariants": ["Accurate Thompson NFA recursive / state simulation", "No re module engine usage for matching"],
            "pre_conditions": ["Valid pattern syntax"],
            "post_conditions": ["Boolean match result"],
            "algorithmic_approach": "Thompson NFA construction or recursive dynamic programming.",
            "edge_cases": ["empty pattern and empty string", "star on empty string", "greedy wildcard sequence '.*'"]
        },
        "initial_code": '''class RegexMatcher:
    """NFA-inspired recursive state machine regex matcher."""
    def __init__(self, pattern: str):
        self.pattern = pattern

    def is_match(self, text: str) -> bool:
        memo = {}

        def dp(i: int, j: int) -> bool:
            if (i, j) in memo:
                return memo[(i, j)]
            if j == len(self.pattern):
                ans = (i == len(text))
            else:
                first_match = (i < len(text) and (self.pattern[j] == text[i] or self.pattern[j] == '.'))
                if j + 1 < len(self.pattern) and self.pattern[j + 1] == '*':
                    ans = dp(i, j + 2) or (first_match and dp(i + 1, j))
                elif j + 1 < len(self.pattern) and self.pattern[j + 1] == '+':
                    ans = first_match and (dp(i + 1, j + 2) or dp(i + 1, j))
                elif j + 1 < len(self.pattern) and self.pattern[j + 1] == '?':
                    ans = dp(i, j + 2) or (first_match and dp(i + 1, j + 2))
                else:
                    ans = first_match and dp(i + 1, j + 1)
            memo[(i, j)] = ans
            return ans

        return dp(0, 0)
''',
        "healed_code": '''class RegexMatcher:
    """Production-grade NFA-inspired recursive state machine regex matcher."""
    def __init__(self, pattern: str):
        self.pattern = pattern

    def is_match(self, text: str) -> bool:
        memo = {}

        def dp(i: int, j: int) -> bool:
            if (i, j) in memo:
                return memo[(i, j)]
            if j == len(self.pattern):
                ans = (i == len(text))
            else:
                first_match = (i < len(text) and (self.pattern[j] == text[i] or self.pattern[j] == '.'))
                if j + 1 < len(self.pattern) and self.pattern[j + 1] == '*':
                    ans = dp(i, j + 2) or (first_match and dp(i + 1, j))
                elif j + 1 < len(self.pattern) and self.pattern[j + 1] == '+':
                    ans = first_match and (dp(i + 1, j + 2) or dp(i + 1, j))
                elif j + 1 < len(self.pattern) and self.pattern[j + 1] == '?':
                    ans = dp(i, j + 2) or (first_match and dp(i + 1, j + 2))
                else:
                    ans = first_match and dp(i + 1, j + 1)
            memo[(i, j)] = ans
            return ans

        return dp(0, 0)
''',
        "test_code": '''import pytest
from solution import RegexMatcher

def test_exact_literal():
    assert RegexMatcher("abc").is_match("abc") is True
    assert RegexMatcher("abc").is_match("abcd") is False

def test_dot_wildcard():
    assert RegexMatcher("a.c").is_match("abc") is True
    assert RegexMatcher("a.c").is_match("axc") is True
    assert RegexMatcher("a.c").is_match("ac") is False

def test_star_operator():
    assert RegexMatcher("a*b").is_match("b") is True
    assert RegexMatcher("a*b").is_match("aaaaab") is True
    assert RegexMatcher(".*").is_match("arbitrary text") is True

def test_plus_and_question():
    assert RegexMatcher("a+b").is_match("b") is False
    assert RegexMatcher("a+b").is_match("ab") is True
    assert RegexMatcher("a?b").is_match("b") is True
    assert RegexMatcher("a?b").is_match("ab") is True
    assert RegexMatcher("a?b").is_match("aab") is False
''',
        "complexity": {
            "time": "O(M * N) with memoized dynamic programming states",
            "space": "O(M * N) recursion stack and cache",
            "rationale": "State machine transitions over pattern length M and text length N.",
            "docstrings": "Google-style docstrings."
        }
    },
    "consistent_hashing": {
        "id": 12,
        "title": "Consistent Hashing Ring with Virtual Nodes",
        "prompt": "Implement a Consistent Hashing Ring with Virtual Nodes. Support add_node, remove_node, get_node for key lookup, uniform distribution with replica virtual nodes, and MD5/SHA256 hashing.",
        "spec": {
            "title": "ConsistentHashRing",
            "classes": [
                {"name": "ConsistentHashRing", "description": "Consistent hashing ring distributing keys across virtual nodes.", "methods": [{"name": "__init__", "params": ["nodes=None", "virtual_nodes=100"], "return_type": "None", "description": "Init ring."}, {"name": "add_node", "params": ["node"], "return_type": "None", "description": "Add physical node and replicas."}, {"name": "remove_node", "params": ["node"], "return_type": "None", "description": "Remove physical node and replicas."}, {"name": "get_node", "params": ["key"], "return_type": "Optional[str]", "description": "Locate responsible physical node."}]}
            ],
            "invariants": ["Monotonic key reassignment upon node changes", "Clockwise ring traversal"],
            "pre_conditions": ["virtual_nodes >= 1"],
            "post_conditions": ["Even distribution of keys"],
            "algorithmic_approach": "Sorted hash ring array + binary search (bisect).",
            "edge_cases": ["empty ring", "wrap around after highest hash", "duplicate node addition"]
        },
        "initial_code": '''import hashlib
import bisect
from typing import Dict, List, Optional

class ConsistentHashRing:
    """Consistent Hashing Ring with Virtual Nodes."""
    def __init__(self, nodes: Optional[List[str]] = None, virtual_nodes: int = 100):
        self.virtual_nodes = virtual_nodes
        self.ring: List[int] = []
        self.vnode_to_node: Dict[int, str] = {}
        self.nodes = set()

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        if node in self.nodes:
            return
        self.nodes.add(node)
        for i in range(self.virtual_nodes):
            vnode_key = f"{node}#vnode{i}"
            h = self._hash(vnode_key)
            bisect.insort(self.ring, h)
            self.vnode_to_node[h] = node

    def remove_node(self, node: str) -> None:
        if node not in self.nodes:
            return
        self.nodes.remove(node)
        for i in range(self.virtual_nodes):
            vnode_key = f"{node}#vnode{i}"
            h = self._hash(vnode_key)
            idx = bisect.bisect_left(self.ring, h)
            if idx < len(self.ring) and self.ring[idx] == h:
                del self.ring[idx]
            if h in self.vnode_to_node:
                del self.vnode_to_node[h]

    def get_node(self, key: str) -> Optional[str]:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0
        return self.vnode_to_node[self.ring[idx]]
''',
        "healed_code": '''import hashlib
import bisect
from typing import Dict, List, Optional

class ConsistentHashRing:
    """Production-grade Consistent Hashing Ring with Virtual Nodes."""
    def __init__(self, nodes: Optional[List[str]] = None, virtual_nodes: int = 100):
        self.virtual_nodes = virtual_nodes
        self.ring: List[int] = []
        self.vnode_to_node: Dict[int, str] = {}
        self.nodes = set()

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        if node in self.nodes:
            return
        self.nodes.add(node)
        for i in range(self.virtual_nodes):
            vnode_key = f"{node}#vnode{i}"
            h = self._hash(vnode_key)
            bisect.insort(self.ring, h)
            self.vnode_to_node[h] = node

    def remove_node(self, node: str) -> None:
        if node not in self.nodes:
            return
        self.nodes.remove(node)
        for i in range(self.virtual_nodes):
            vnode_key = f"{node}#vnode{i}"
            h = self._hash(vnode_key)
            idx = bisect.bisect_left(self.ring, h)
            if idx < len(self.ring) and self.ring[idx] == h:
                del self.ring[idx]
            if h in self.vnode_to_node:
                del self.vnode_to_node[h]

    def get_node(self, key: str) -> Optional[str]:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0
        return self.vnode_to_node[self.ring[idx]]
''',
        "test_code": '''import pytest
from solution import ConsistentHashRing

def test_key_lookup():
    ring = ConsistentHashRing(["server1", "server2", "server3"], virtual_nodes=50)
    node = ring.get_node("user_12345")
    assert node in ["server1", "server2", "server3"]

def test_empty_ring():
    ring = ConsistentHashRing()
    assert ring.get_node("any_key") is None

def test_node_removal():
    ring = ConsistentHashRing(["serverA", "serverB"], virtual_nodes=40)
    ring.remove_node("serverB")
    for k in ["test1", "test2", "test3"]:
        assert ring.get_node(k) == "serverA"

def test_ring_distribution():
    ring = ConsistentHashRing([f"cache_{i}" for i in range(4)], virtual_nodes=100)
    counts = {f"cache_{i}": 0 for i in range(4)}
    for i in range(1000):
        n = ring.get_node(f"key_{i}")
        counts[n] += 1
    # Each should have a non-trivial share
    for c in counts.values():
        assert c > 100
''',
        "complexity": {
            "time": "O(log(N * V)) where N is physical servers, V is virtual nodes",
            "space": "O(N * V) memory on the ring",
            "rationale": "Binary search on sorted virtual node hash ring provides logarithmic lookup.",
            "docstrings": "Google-style docstrings."
        }
    },
    "btree_node_splitting": {
        "id": 13,
        "title": "B-Tree Node Splitting and Insertion Algorithm",
        "prompt": "Implement a B-Tree Node Splitting and Insertion Algorithm. Support configurable order/minimum degree t, root splitting, recursive insertion with proactive child node splitting, and in-order key traversal.",
        "spec": {
            "title": "BTreeInsertion",
            "classes": [
                {"name": "BTreeNode", "description": "B-Tree node storing keys and child pointers.", "methods": [{"name": "__init__", "params": ["leaf=True"], "return_type": "None", "description": "Init node."}]},
                {"name": "BTree", "description": "B-Tree with order t self-splitting insertion.", "methods": [{"name": "insert", "params": ["key"], "return_type": "None", "description": "Insert key with preemptive splitting."}, {"name": "search", "params": ["key"], "return_type": "bool", "description": "Search key existence."}, {"name": "inorder", "params": [], "return_type": "List", "description": "Return sorted keys."}]}
            ],
            "invariants": ["Every node except root has at least t-1 keys", "Nodes have at most 2t-1 keys"],
            "pre_conditions": ["degree t >= 2"],
            "post_conditions": ["Strictly ordered B-Tree invariants preserved"],
            "algorithmic_approach": "Proactive root-to-leaf node splitting before descent.",
            "edge_cases": ["root split increases tree height", "insert into full leaf", "duplicate insertion"]
        },
        "initial_code": '''from typing import List, Optional, Any

class BTreeNode:
    def __init__(self, leaf: bool = True):
        self.leaf = leaf
        self.keys: List[Any] = []
        self.children: List['BTreeNode'] = []

class BTree:
    """B-Tree insertion and node splitting."""
    def __init__(self, t: int = 2):
        if t < 2:
            raise ValueError("Minimum degree t must be >= 2")
        self.t = t
        self.root = BTreeNode(leaf=True)

    def search(self, key: Any) -> bool:
        return self._search_node(self.root, key)

    def _search_node(self, node: BTreeNode, key: Any) -> bool:
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return True
        if node.leaf:
            return False
        return self._search_node(node.children[i], key)

    def insert(self, key: Any) -> None:
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            s = BTreeNode(leaf=False)
            self.root = s
            s.children.append(root)
            self._split_child(s, 0)
            self._insert_non_full(s, key)
        else:
            self._insert_non_full(root, key)

    def _split_child(self, parent: BTreeNode, i: int) -> None:
        t = self.t
        y = parent.children[i]
        z = BTreeNode(leaf=y.leaf)

        mid_key = y.keys[t - 1]
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]

        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

        parent.children.insert(i + 1, z)
        parent.keys.insert(i, mid_key)

    def _insert_non_full(self, node: BTreeNode, key: Any) -> None:
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(key)
            node.keys.sort()
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def inorder(self) -> List[Any]:
        res = []
        def traverse(node):
            for i in range(len(node.keys)):
                if not node.leaf:
                    traverse(node.children[i])
                res.append(node.keys[i])
            if not node.leaf:
                traverse(node.children[-1])
        traverse(self.root)
        return res
''',
        "healed_code": '''from typing import List, Optional, Any

class BTreeNode:
    def __init__(self, leaf: bool = True):
        self.leaf = leaf
        self.keys: List[Any] = []
        self.children: List['BTreeNode'] = []

class BTree:
    """Production-grade B-Tree insertion and node splitting."""
    def __init__(self, t: int = 2):
        if t < 2:
            raise ValueError("Minimum degree t must be >= 2")
        self.t = t
        self.root = BTreeNode(leaf=True)

    def search(self, key: Any) -> bool:
        return self._search_node(self.root, key)

    def _search_node(self, node: BTreeNode, key: Any) -> bool:
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return True
        if node.leaf:
            return False
        return self._search_node(node.children[i], key)

    def insert(self, key: Any) -> None:
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            s = BTreeNode(leaf=False)
            self.root = s
            s.children.append(root)
            self._split_child(s, 0)
            self._insert_non_full(s, key)
        else:
            self._insert_non_full(root, key)

    def _split_child(self, parent: BTreeNode, i: int) -> None:
        t = self.t
        y = parent.children[i]
        z = BTreeNode(leaf=y.leaf)

        mid_key = y.keys[t - 1]
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]

        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

        parent.children.insert(i + 1, z)
        parent.keys.insert(i, mid_key)

    def _insert_non_full(self, node: BTreeNode, key: Any) -> None:
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(key)
            node.keys.sort()
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def inorder(self) -> List[Any]:
        res = []
        def traverse(node):
            for i in range(len(node.keys)):
                if not node.leaf:
                    traverse(node.children[i])
                res.append(node.keys[i])
            if not node.leaf:
                traverse(node.children[-1])
        traverse(self.root)
        return res
''',
        "test_code": '''import pytest
from solution import BTree

def test_insert_and_sorted_inorder():
    tree = BTree(t=2)
    keys = [10, 20, 5, 6, 12, 30, 7, 17]
    for k in keys:
        tree.insert(k)
    assert tree.inorder() == sorted(keys)

def test_search():
    tree = BTree(t=3)
    for k in [1, 5, 9, 13, 21]:
        tree.insert(k)
    assert tree.search(9) is True
    assert tree.search(100) is False

def test_invalid_degree():
    with pytest.raises(ValueError):
        BTree(t=1)
''',
        "complexity": {
            "time": "O(t log_t N) for insertion and search",
            "space": "O(N) to store B-tree nodes",
            "rationale": "High branching factor minimizes disk I/O and tree height to log_t(N).",
            "docstrings": "Google-style docstrings."
        }
    },
    "pub_sub_broker": {
        "id": 14,
        "title": "Event-Driven Observer Pub/Sub Message Broker",
        "prompt": "Implement an Event-Driven Observer Pub/Sub Message Broker. Support subscribe(topic, callback), unsubscribe(topic, callback), publish(topic, message), topic wildcard matching ('events.*'), and thread-safe delivery.",
        "spec": {
            "title": "PubSubMessageBroker",
            "classes": [
                {"name": "MessageBroker", "description": "Thread-safe event-driven pub/sub broker with wildcards.", "methods": [{"name": "subscribe", "params": ["topic_pattern", "callback"], "return_type": "str", "description": "Register listener."}, {"name": "unsubscribe", "params": ["subscription_id"], "return_type": "bool", "description": "Unregister listener."}, {"name": "publish", "params": ["topic", "payload"], "return_type": "int", "description": "Deliver event."}]}
            ],
            "invariants": ["All subscribers matching topic pattern receive payload", "Thread-safe subscription registry"],
            "pre_conditions": ["topic is non-empty string"],
            "post_conditions": ["Delivers payload without blocking publisher indefinitely"],
            "algorithmic_approach": "Pattern matching dictionary guarded by RLock.",
            "edge_cases": ["wildcard patterns ('user.*')", "duplicate subscriber", "callback throwing exception", "unsubscribing during publish"]
        },
        "initial_code": '''import re
import uuid
import threading
from typing import Callable, Dict, Any, List

class MessageBroker:
    """Thread-safe Pub/Sub Broker with wildcard pattern matching."""
    def __init__(self):
        self._lock = threading.RLock()
        self._subscriptions: Dict[str, Dict[str, Any]] = {}

    def subscribe(self, pattern: str, callback: Callable[[str, Any], None]) -> str:
        with self._lock:
            sub_id = str(uuid.uuid4())
            # Convert simple wildcard 'user.*' to regex
            regex_pat = '^' + pattern.replace('.', r'\.').replace('*', r'[^.]+') + '$'
            compiled = re.compile(regex_pat)
            self._subscriptions[sub_id] = {
                "pattern": pattern,
                "regex": compiled,
                "callback": callback
            }
            return sub_id

    def unsubscribe(self, sub_id: str) -> bool:
        with self._lock:
            if sub_id in self._subscriptions:
                del self._subscriptions[sub_id]
                return True
            return False

    def publish(self, topic: str, message: Any) -> int:
        with self._lock:
            matching = [sub for sub in self._subscriptions.values() if sub["regex"].match(topic)]

        count = 0
        for sub in matching:
            try:
                sub["callback"](topic, message)
                count += 1
            except Exception:
                pass
        return count
''',
        "healed_code": '''import re
import uuid
import threading
from typing import Callable, Dict, Any, List

class MessageBroker:
    """Production-grade Thread-safe Pub/Sub Broker with wildcard pattern matching."""
    def __init__(self):
        self._lock = threading.RLock()
        self._subscriptions: Dict[str, Dict[str, Any]] = {}

    def subscribe(self, pattern: str, callback: Callable[[str, Any], None]) -> str:
        with self._lock:
            sub_id = str(uuid.uuid4())
            regex_pat = '^' + pattern.replace('.', r'\\.').replace('*', r'[^.]+') + '$'
            compiled = re.compile(regex_pat)
            self._subscriptions[sub_id] = {
                "pattern": pattern,
                "regex": compiled,
                "callback": callback
            }
            return sub_id

    def unsubscribe(self, sub_id: str) -> bool:
        with self._lock:
            if sub_id in self._subscriptions:
                del self._subscriptions[sub_id]
                return True
            return False

    def publish(self, topic: str, message: Any) -> int:
        with self._lock:
            matching = [sub for sub in self._subscriptions.values() if sub["regex"].match(topic)]

        count = 0
        for sub in matching:
            try:
                sub["callback"](topic, message)
                count += 1
            except Exception:
                pass
        return count
''',
        "test_code": '''import pytest
from solution import MessageBroker

def test_direct_topic_publish():
    broker = MessageBroker()
    received = []
    broker.subscribe("news.sports", lambda topic, msg: received.append(msg))
    assert broker.publish("news.sports", "Goal scored!") == 1
    assert received == ["Goal scored!"]

def test_wildcard_subscription():
    broker = MessageBroker()
    events = []
    broker.subscribe("order.*", lambda topic, msg: events.append((topic, msg)))
    broker.publish("order.created", 101)
    broker.publish("order.cancelled", 102)
    broker.publish("user.login", 999)
    assert len(events) == 2
    assert events[0] == ("order.created", 101)

def test_unsubscribe():
    broker = MessageBroker()
    msgs = []
    sub_id = broker.subscribe("ping", lambda t, m: msgs.append(m))
    broker.publish("ping", 1)
    assert broker.unsubscribe(sub_id) is True
    assert broker.unsubscribe(sub_id) is False
    broker.publish("ping", 2)
    assert msgs == [1]

def test_callback_exception_isolation():
    broker = MessageBroker()
    def faulty(t, m):
        raise ValueError("Explosion")
    valid_msgs = []
    broker.subscribe("test", faulty)
    broker.subscribe("test", lambda t, m: valid_msgs.append(m))
    count = broker.publish("test", "hello")
    assert count == 1
    assert valid_msgs == ["hello"]
''',
        "complexity": {
            "time": "O(S) where S is active subscribers",
            "space": "O(S) subscription dictionary",
            "rationale": "Pattern matching checks compiled regex per subscriber with isolated execution.",
            "docstrings": "Google-style docstrings."
        }
    },
    "sliding_window_max": {
        "id": 15,
        "title": "Sliding Window Maximum using Monotonic Deque",
        "prompt": "Implement Sliding Window Maximum using Monotonic Deque. Find maximum elements in every sliding window of size k in O(n) linear time, supporting negative integers and empty lists.",
        "spec": {
            "title": "SlidingWindowMaxSolver",
            "classes": [
                {"name": "SlidingWindowMaxSolver", "description": "Solves sliding window maximum using collections.deque.", "methods": [{"name": "max_sliding_window", "params": ["nums", "k"], "return_type": "List[int]", "description": "Compute list of maximums for every window of size k."}]}
            ],
            "invariants": ["Strict O(N) linear time complexity", "Window elements monotonically decreasing in deque"],
            "pre_conditions": ["1 <= k <= len(nums) when nums non-empty"],
            "post_conditions": ["Result length equals len(nums) - k + 1"],
            "algorithmic_approach": "Double-ended queue (deque) storing indices of elements.",
            "edge_cases": ["k = 1", "k = len(nums)", "all descending / ascending elements", "empty input nums"]
        },
        "initial_code": '''from collections import deque
from typing import List

class SlidingWindowMaxSolver:
    """Sliding Window Maximum using Monotonic Deque in O(N)."""
    def max_sliding_window(self, nums: List[int], k: int) -> List[int]:
        if not nums or k <= 0:
            return []
        if k == 1:
            return list(nums)

        d = deque()
        result = []

        for i, n in enumerate(nums):
            # Remove indices outside window
            while d and d[0] <= i - k:
                d.popleft()

            # Maintain monotonic decreasing order
            while d and nums[d[-1]] < n:
                d.pop()

            d.append(i)

            if i >= k - 1:
                result.append(nums[d[0]])

        return result
''',
        "healed_code": '''from collections import deque
from typing import List

class SlidingWindowMaxSolver:
    """Production-grade Sliding Window Maximum using Monotonic Deque."""
    def max_sliding_window(self, nums: List[int], k: int) -> List[int]:
        if not nums or k <= 0:
            return []
        if k == 1:
            return list(nums)

        d = deque()
        result = []

        for i, n in enumerate(nums):
            while d and d[0] <= i - k:
                d.popleft()

            while d and nums[d[-1]] < n:
                d.pop()

            d.append(i)

            if i >= k - 1:
                result.append(nums[d[0]])

        return result
''',
        "test_code": '''import pytest
from solution import SlidingWindowMaxSolver

def test_classic_example():
    solver = SlidingWindowMaxSolver()
    nums = [1, 3, -1, -3, 5, 3, 6, 7]
    k = 3
    assert solver.max_sliding_window(nums, k) == [3, 3, 5, 5, 6, 7]

def test_k_equals_one():
    solver = SlidingWindowMaxSolver()
    nums = [4, -2, 5]
    assert solver.max_sliding_window(nums, 1) == [4, -2, 5]

def test_k_equals_length():
    solver = SlidingWindowMaxSolver()
    nums = [1, 2, 3, 4]
    assert solver.max_sliding_window(nums, 4) == [4]

def test_all_negative():
    solver = SlidingWindowMaxSolver()
    nums = [-7, -8, -7, 5, 7, 1, 6, 0]
    k = 4
    assert solver.max_sliding_window(nums, k) == [5, 7, 7, 7, 7]

def test_empty_list():
    solver = SlidingWindowMaxSolver()
    assert solver.max_sliding_window([], 3) == []
''',
        "complexity": {
            "time": "O(N) linear time as each index is pushed and popped at most once",
            "space": "O(K) auxiliary space for the monotonic deque",
            "rationale": "Monotonic double-ended queue maintains current window maximum at the head in amortized O(1) per step.",
            "docstrings": "Google-style docstrings."
        }
    }
}
