-- @todo has never been debugged

local node=KEYS[1]
local message=ARGV[1]
local tags = ARGV[2]
local level = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

local v= {}

v["node"]= node
v["message"]= message
v["tags"]= tags
v["level"]= level
v["epoch"]= now
redis.call('HSET',hsetkey,KEYS[1],)

if redis.call("LLEN", "queues:logs") > 5000 then
    redis.call("LPOP", "qeues:logs")
end

redis.call("RPUSH", "queues:logs",cjson.encode(v))
return "OK"

