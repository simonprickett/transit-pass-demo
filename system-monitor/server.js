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

r.on(`pass-activated:${PASS_TYPE_TWO_HOUR}`, (msg) => {
  console.log(chalk.magenta(`Card ${msg.cardSerialNumber} two hour pass activated.`))
})

r.on('pass-used:*', (msg) => {
  // some type of pass used
  console.log(chalk.blue(`Card ${msg.cardSerialNumber} started a journey.`))
})

r.on(`pass-used:${PASS_TYPE_TEN_TRIP}`, (msg) => {
  console.log(chalk.yellow(`Card ${msg.cardSerialNumber} has ${msg.remainingTrips} of 10 trips remaining.`))
})

r.on('pass-denied', (msg) => {
  console.log(chalk.red(`Card ${msg.cardSerialNumber} tried to start a journey without a valid pass!`))
})