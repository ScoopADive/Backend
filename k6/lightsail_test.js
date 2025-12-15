import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
          vus: 100,
          duration: '2m',
};

export default function () {
          http.get('https://scoopadive.com'); // Lightsail에서 프론트 서빙 중인 주>소
          sleep(0.5);
}
