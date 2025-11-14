import http from "k6/http";
import { check, sleep } from "k6";

const BASE = "https://scoopadive.com";  // 실제 서버 주소

export let options = {
    vus: 10,         // 동시에 10명 가상 사용자
    duration: "30s", // 30초 동안 테스트
};

export default function () {
    // 1️⃣ 로그인
    const loginPayload = JSON.stringify({
        email: "ruby@gmail.com",
        password: "12345678"
    });

    const loginHeaders = { "Content-Type": "application/json" };
    const loginRes = http.post(`${BASE}/api/auths/signin/`, loginPayload, { headers: loginHeaders });

    if (loginRes.status !== 200) {
        console.error("Login failed!");
        return;
    }

    const accessToken = loginRes.json("access"); // 서버 JSON 구조에 맞게 조정

    // 2️⃣ likes_async API 요청
    const apiHeaders = {
        "Authorization": `Bearer ${accessToken}`,
    };

    const res = http.get(`${BASE}/api/logbooks/likes_async/`, { headers: apiHeaders });

    check(res, { "status was 200": (r) => r.status === 200 });

    sleep(1); // 1초 쉬고 다음 반복
}
