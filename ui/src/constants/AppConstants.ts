/*
Here, you can mention the FASTAPI endpoint
*/
import data from './../../../config.json';

export const AppConstants = {
  BACKEND_BASE_URL: 'http://127.0.0.1:' + data.port,
  BACKEND_PORT: 4000,
}
