import http from "k6/http";
import { check } from "k6";

const BASE = "https://scoopadive.com";

export default function () {
  // 1️⃣ 로그인
  const loginPayload = JSON.stringify({
    email: "ruby@gmail.com",
    password: "12345678"
  });

  const loginHeaders = { "Content-Type": "application/json" };
  const loginRes = http.post(`${BASE}/api/auths/signin/`, loginPayload, { headers: loginHeaders });

  check(loginRes, { "login succeeded": (r) => r.status === 200 });

  const accessToken = loginRes.json("access");

  // 2️⃣ API 요청
  const apiHeaders = {
    "Authorization": `Bearer ${accessToken}`,
  };

  const res = http.get(`${BASE}/api/logbooks/likes/`, { headers: apiHeaders });

  check(res, { "status was 200": (r) => r.status === 200 });
}
