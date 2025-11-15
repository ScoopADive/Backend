import http from "k6/http";
import { check, sleep } from "k6";
                                                                                                                 2025-11-
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
                                                                                                                 16a700>
        const token = loginRes.json("access");
        return { token };                                                                                        x71b8451
}
                                                                                                                 ntext of
export default function (data) {
        const apiHeaders = {
                "Authorization": `Bearer ${data.token}`,                                                         b240>
                "Content-Type": "application/json"                                                               otocore.
        };
                                                                                                                 e, 'UseD
        const res = http.get(`${BASE}/api/logbooks/likes/`, { headers: apiHeaders });                            essPoint

        check(res, { "status was 200": (r) => r.status === 200 });

        sleep(1);                                                                                                leDouble
}