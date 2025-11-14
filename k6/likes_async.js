import http from "k6/http";
import { check, sleep } from "k6";

export let options = {
    vus: 50,
    duration: "45s",
};

const BASE = "https://scoopadive.com";

export default function () {

    const login = http.post(
        `${BASE}/api/auths/login/`,
        JSON.stringify({
            email: "ruby@gmail.com",
            password: "12345678",
        }),
        { headers: { "Content-Type": "application/json" } }
    );

    const token = login.json("access");

    // async endpoint
    const res = http.get(`${BASE}/api/logbooks/likes_async/`, {
        headers: { Authorization: `Bearer ${token}` },
    });

    check(res, {
        "status 200": (r) => r.status === 200,
    });

    sleep(0.3);
}

