const chalk = require('chalk')
const nrp = require('node-redis-pubsub')

const r = new nrp({
  host: process.env.TRANSIT_PASS_DEMO_REDIS_HOST,
  port: process.env.TRANSIT_PASS_DEMO_REDIS_PORT,
  auth: process.env.TRANSIT_PASS_DEMO_REDIS_PASSWORD
})

const PASS_TYPE_SINGLE_USE = 'SINGLE_USE'
const PASS_TYPE_TWO_HOUR = 'TWO_HOUR'
const PASS_TYPE_TEN_TRIP = 'TEN_TRIP'

const decodePassType = (passType) => {
  switch (passType) {
    case PASS_TYPE_SINGLE_USE:
      return 'single trip'
    case PASS_TYPE_TWO_HOUR:
      return 'two hour'
    case PASS_TYPE_TEN_TRIP:
      return 'ten trip'
  }
}

r.on('pass-issued:*', (msg) => {
  console.log(chalk.yellow(`Card ${msg.cardSerialNumber} was issued a ${decodePassType(msg.pass.passType)} pass.`))
})

r.on('pass-issued:TEN_TRIP', (msg) => {
  console.log('This would be an extra action only for the ten trip pass...')  
})