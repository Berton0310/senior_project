const http = require('http')
const WebSocket = require('ws')
const Y = require('yjs')
const { setupWSConnection } = require('y-websocket/bin/utils')
const fetch = require('node-fetch')

const server = http.createServer()
const wss = new WebSocket.Server({ server })
wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    // 廣播訊息給所有連接的客戶端
    wss.clients.forEach((client) => {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(message)
      }
    })
  })
})
server.listen(1235, () => {
  console.log('協同編輯伺服器運行在端口 1234')
})
