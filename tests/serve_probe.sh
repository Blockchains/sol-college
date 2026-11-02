#!/usr/bin/env bash
# usage: serve_probe.sh <port> <path> <start command...>  -- starts a server, waits for HTTP 200 on the path, prints a title line, stops it.
port=$1; path=$2; shift 2
( exec "$@" ) > /tmp/serve_$port.log 2>&1 &
pid=$!
for i in $(seq 1 90); do
  code=$(curl -sL -o /tmp/serve_$port.html -w '%{http_code}' "http://localhost:$port$path")
  [ "$code" = 200 ] && break; sleep 2
done
echo "GET http://localhost:$port$path -> $code"
grep -o '<title>[^<]*' /tmp/serve_$port.html | head -1
kill $pid 2>/dev/null; pkill -P $pid 2>/dev/null; fuser -k $port/tcp >/dev/null 2>&1
[ "$code" = 200 ]
