-- @todo has never been debugged

local key=KEYS[1]
local json =ARGV[1]
local node =ARGV[2]
local tags = ARGV[3]
local now = tonumber(ARGV[4])
local modeltype = ARGV[5]

local v= {}

v["key"]= key
v["node"]= node
v["json"]= json
v["tags"]= tags
v["epoch"]= now
v["modeltype"] = modeltype

data= cjson.encode(v)

redis.call('HSET',hsetkey,key,data)

if redis.call("LLEN", "queues:reality") > 5000 then
    redis.call("LPOP", "qeues:reality")
end

-- this allows multiple consumers to get the data of a queue & process
redis.call("RPUSH", "queues:reality",data)
return "OK"

