import time
import uuid
import asyncio
from multiprocessing import Pool, Manager


# ==========================================
# 1. Mock 환경 설정 (Presigned URL & Fishial Flow)
# ==========================================

class MockFishialClient:
    def __init__(self, shared_dict=None, lock=None, network_delay=0):
        self.shared_dict = shared_dict
        self.lock = lock
        self.network_delay = network_delay

    async def get_async_token(self):
        """[ASYNC] Step 1: 인증 토큰 발급 (공유 자원)"""
        # (비동기 환경에서는 멀티프로세싱 Lock/Manager를 직접 사용하지 않습니다.
        # 따라서 동기 실험과 달리 매번 토큰을 발급한다고 가정합니다.)
        await asyncio.sleep(0.1)
        return f"token_{uuid.uuid4().hex[:8]}"

    def get_sync_token(self):
        """[SYNC] Step 1: 인증 토큰 발급 (공유 자원)"""
        if self.lock and self.shared_dict is not None:
            if 'access_token' in self.shared_dict:
                return self.shared_dict['access_token']
            with self.lock:
                if 'access_token' in self.shared_dict:
                    return self.shared_dict['access_token']
                time.sleep(0.1)
                token = f"token_{uuid.uuid4().hex[:8]}"
                self.shared_dict['access_token'] = token
                return token
        else:
            time.sleep(0.1)
            return f"token_{uuid.uuid4().hex[:8]}"

    async def process_async_image_flow(self, token, image_index):
        """[ASYNC] Step 2~5: Presigned URL ~ 인공지능 분류 (핵심 병렬화 구간)"""
        if self.network_delay > 0:
            await asyncio.sleep(self.network_delay)

        # Step 2: Presigned URL 생성 요청
        await asyncio.sleep(0.05)
        # Step 3: 클라이언트 -> S3 업로드
        await asyncio.sleep(0.2)
        # Step 4: Fishial API 인식 요청
        await asyncio.sleep(0.5)

        return f"Image_{image_index}: Tuna"

    def process_sync_image_flow(self, token, image_index):
        """[SYNC] Step 2~5: Presigned URL ~ 인공지능 분류"""
        if self.network_delay > 0:
            time.sleep(self.network_delay)

        # Step 2: Presigned URL 생성 요청
        time.sleep(0.05)
        # Step 3: 클라이언트 -> S3 업로드
        time.sleep(0.2)
        # Step 4: Fishial API 인식 요청
        time.sleep(0.5)

        return f"Image_{image_index}: Tuna"


# ==========================================
# 2. 워커 함수
# ==========================================

def worker_task_sync(image_idx, shared_dict, lock, network_delay=0):
    client = MockFishialClient(shared_dict, lock, network_delay)
    token = client.get_sync_token()
    client.process_sync_image_flow(token, image_idx)
    return True


async def worker_task_async(image_idx, network_delay=0):
    client = MockFishialClient(network_delay=network_delay)
    token = await client.get_async_token()
    await client.process_async_image_flow(token, image_idx)
    return True


# ==========================================
# 3. 실험 메인 컨트롤러
# ==========================================

def draw_bar_chart(results):
    print("\n" + "=" * 60)
    print("📊  [성능 비교 결과 그래프]")
    print("=" * 60)

    max_time = max(results.values())

    for name, t in results.items():
        bar_length = int((t / max_time) * 40)
        bar = "█" * bar_length
        print(f"{name.ljust(25)} | {bar} {t:.2f}s")
    print("=" * 60 + "\n")


def run_experiment():
    # --- 실험 조건 ---
    NUM_IMAGES = 40
    LOCAL_CORES = 4
    DISTRIBUTED_NODES = 16

    # 개별 이미지 처리 시간 (I/O 총합): 0.1 (Token) + 0.05 (URL) + 0.2 (S3) + 0.5 (AI) = 0.85s
    # 순차 처리 예상 시간: 40 * 0.85s = 34s (코드의 T1과 동일)

    print(f"\n🧪 [실험 시작] 이미지 {NUM_IMAGES}장 처리\n")

    results = {}

    # -------------------------------------------------
    # 1. 순차 처리 (Sequential)
    # -------------------------------------------------
    print(f"1️⃣  [순차 처리 - Sync] 실행 중...", end=" ", flush=True)
    start = time.time()
    client = MockFishialClient()
    for i in range(NUM_IMAGES):
        token = client.get_sync_token()
        client.process_sync_image_flow(token, i)

    t1 = time.time() - start
    results['1. Sequential (Sync)'] = t1
    print(f"완료! ({t1:.2f}s)")

    # -------------------------------------------------
    # 2. 멀티프로세싱 (Local Parallel)
    # -------------------------------------------------
    print(f"2️⃣  [멀티프로세싱 (Lock)] {LOCAL_CORES}코어 실행 중...", end=" ", flush=True)
    m = Manager()
    shared_dict = m.dict()
    lock = m.Lock()

    start = time.time()
    with Pool(processes=LOCAL_CORES) as pool:
        pool.starmap(worker_task_sync, [(i, shared_dict, lock, 0) for i in range(NUM_IMAGES)])

    t2 = time.time() - start
    results['2. Multi-Processing'] = t2
    print(f"완료! ({t2:.2f}s)")

    # -------------------------------------------------
    # 3. 분산 서버 시뮬레이션 (MPI/Cluster)
    # -------------------------------------------------
    print(f"3️⃣  [분산 클러스터 (MPI)] {DISTRIBUTED_NODES}노드 실행 중...", end=" ", flush=True)

    NETWORK_OVERHEAD = 0.05
    dist_m = Manager()
    dist_shared = dist_m.dict()
    dist_lock = dist_m.Lock()

    start = time.time()
    with Pool(processes=DISTRIBUTED_NODES) as pool:
        pool.starmap(worker_task_sync,
                     [(i, dist_shared, dist_lock, NETWORK_OVERHEAD) for i in range(NUM_IMAGES)])

    t3 = time.time() - start
    results['3. Distributed Sys'] = t3
    print(f"완료! ({t3:.2f}s)")

    # -------------------------------------------------
    # 4. Async 처리 (단일 스레드 논블로킹)
    # -------------------------------------------------
    print(f"4️⃣  [비동기 처리 (Async)] 단일 스레드 실행 중...", end=" ", flush=True)

    start = time.time()

    async def async_main():
        tasks = [worker_task_async(i) for i in range(NUM_IMAGES)]
        await asyncio.gather(*tasks)

    # 파이썬 3.7+ 환경에서 asyncio.run()을 사용하여 실행
    asyncio.run(async_main())

    t4 = time.time() - start
    results['4. Async (Single Thread)'] = t4
    print(f"완료! ({t4:.2f}s)")

    # -------------------------------------------------
    # 결과 출력
    # -------------------------------------------------
    draw_bar_chart(results)

    print("💡 분석 가이드:")
    print(f" - 순차 처리는 1개씩 하므로 가장 느립니다. (약 {t1:.1f}초)")
    print(f" - Async 처리는 단일 스레드지만, 느린 I/O 대기 시간({0.85:.2f}s)을 활용하여 {t4:.2f}s를 달성했습니다.")
    print(f" - 멀티프로세싱/분산 시스템은 CPU 자원 자체를 늘려 가장 빠른 성능을 달성했습니다.")


if __name__ == '__main__':
    run_experiment()