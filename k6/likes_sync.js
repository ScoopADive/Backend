import http from "k6/http";
import { check, sleep } from "k6";

export let options = {
    vus: 50,
    duration: "45s",
};

const BASE = "https://scoopadive.com";

export default function () {

    // 1) 로그인
    const login = http.post(
        `${BASE}/api/auths/login/`,
        JSON.stringify({
            email: "ruby@gmail.com",
            password: "12345678",
        }),
        { headers: { "Content-Type": "application/json" } }
    );

    const token = login.json("access");

    // 2) sync API 호출
    const res = http.get(`${BASE}/api/logbooks/likes/`, {
        headers: { Authorization: `Bearer ${token}` },
    });

    check(res, {
        "status 200": (r) => r.status === 200,
    });

    sleep(0.3);
}

