const redis = require('redis')
const r = redis.createClient({
    host: process.env.TRANSIT_PASS_DEMO_REDIS_HOST,
    port: process.env.TRANSIT_PASS_DEMO_REDIS_PORT,
    password: process.env.TRANSIT_PASS_DEMO_REDIS_PASSWORD
})