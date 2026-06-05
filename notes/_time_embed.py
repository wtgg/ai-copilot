"""临时测 bge-m3 加载时间(可删)"""
import time

t0 = time.time()
print("importing EmbeddingService...")
from app.services.rag.embedding import EmbeddingService
print(f"  import done in {time.time() - t0:.2f}s")

t0 = time.time()
print("instantiating EmbeddingService (will load bge-m3)...")
e = EmbeddingService()
print(f"  loaded in {time.time() - t0:.2f}s")

t0 = time.time()
print("embedding a tiny query...")
v = e.embed_query("hello")
print(f"  embedded in {time.time() - t0:.2f}s, dim={len(v)}")
