
local message=KEYS[1]
local messagepub=ARGV[1]
local level = tonumber(ARGV[2])
local type = ARGV[3]
local tags = ARGV[4]
local code = ARGV[5]
local funcname = ARGV[6]
local funcfilepath = ARGV[7]
local backtrace = ARGV[8]
local newtime = tonumber(ARGV[9])

local eco= {}

--dont know what md5 function is in lua, so this is pseudocode needs to be fixed todo (*1*) Azmy
key=md5(message+messagepub+code+funcname+funcfilepath)

if redis.call("HEXISTS", "eco:objects",key)==1 then
    local ecoraw=redis.call("HGET", "eco:objects",key)
    local eco=cjson.decode(ecoraw)
    eco["occurrences"]=eco["occurrences"]+1
    lasttime = eco["lasttime"]
    eco["lasttime"]=newtime

    if lasttime<(newtime-300) then
        --more than 5 min ago, lets put on queue again
        redis.call("RPUSH", "queues:eco",key)
    end

else
    eco["key"] = key
    eco["message"]= message
    eco["messagepub"]= messagepub
    eco["code"]= code
    eco["funcname"]= funcname
    eco["funcfilepath"]= funcfilepath
    eco["lasttime"]= now
    eco["closetime"]= 0
    eco["occurrences"]= 1
end

--overwrite even the ones coming from DB
eco["backtrace"]= backtrace
eco["level"]= level
eco["type"]= type
eco["tags"]= tags


local ecoraw=cjson.encode(eco)

redis.call("HSET", "eco:objects",key,ecoraw)
-- need to set expiration on the object, let it expire after 7 days

if redis.call("LLEN", "queues:eco") > 1000 then
    local todelete = redis.call("LPOP", "queues:eco")
    redis.call("HDEL","eco:objects",todelete)
end

-- last resort
if redis.call("HLEN", "eco:objects") > 10000 then
    redis.call("DEL", "eco:objects")
end


return ecoraw
