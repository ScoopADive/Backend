import http from "k6/http";
import { check, sleep } from "k6";

const BASE = "https://scoopadive.com";

export let options = {
        vus: 50,
        duration: "30s",
};

export function setup() {
        const loginPayload = JSON.stringify({
                email: "ruby@gmail.com",
                password: "12345678"
        });

        const loginHeaders = { "Content-Type": "application/json" };
        const loginRes = http.post(`${BASE}/api/auths/signin/`, loginPayload, { headers: loginHeaders });

        check(loginRes, { "login succeeded": (r) => r.status === 200 && r.json("access") !== undefined });

        const token = loginRes.json("access");
        return { token };
}

export default function (data) {
        const apiHeaders = {
                "Authorization": `Bearer ${data.token}`,
                "Content-Type": "application/json"
        };

        const res = http.get(`${BASE}/api/logbooks/likes_async/`, { headers: apiHeaders });

        check(res, { "status was 200": (r) => r.status === 200 });

        sleep(1);
}