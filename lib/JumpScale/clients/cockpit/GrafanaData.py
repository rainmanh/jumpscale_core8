datasource = {
            "name": "influxdb_main",
            "type": "influxdb",
            "access": "proxy",
            "url": "http://localhost:8086",
            "password": "asd",
            "user": "ad",
            "database": "statistics",
            "basicAuth": False,
            "basicAuthUser": "",
            "basicAuthPassword":"",
            "withCredentials":False,
            "isDefault":False
}

dashboard = {
    "dashboard": {
        "title": "Nodes stats",
        "originalTitle": "New dashboard",
        "tags": [],
        "style": "dark",
        "timezone": "browser",
        "editable": True,
        "hideControls": False,
        "sharedCrosshair": False,
        "rows": [
            {
                "collapse": False,
                "editable": True,
                "height": "250px",
                "panels": [
                    {
                        "aliasColors": {},
                        "bars": False,
                        "datasource": "influxdb_main",
                        "editable": True,
                        "error": False,
                        "fill": 1,
                        "grid": {
                            "leftLogBase": 1,
                            "rightLogBase": 1,
                            "threshold1Color": "rgba(216, 200, 27, 0.27)",
                            "threshold2Color": "rgba(234, 112, 112, 0.22)"
                        },
                        "id": 1,
                        "isNew": True,
                        "legend": {
                            "avg": False,
                            "current": False,
                            "max": False,
                            "min": False,
                            "show": True,
                            "total": False,
                            "values": False
                        },
                        "lines": True,
                        "linewidth": 2,
                        "percentage": False,
                        "pointradius": 5,
                        "points": False,
                        "renderer": "flot",
                        "seriesOverrides": [],
                        "span": 12,
                        "stack": False,
                        "steppedLine": False,
                        "targets": [
                            {
                                "dsType": "influxdb",
                                "groupBy": [
                                    {
                                        "params": [
                                            "node"
                                        ],
                                        "type": "tag"
                                    }
                                ],
                                "measurement": "cpu.percent|m",
                                "query": "SELECT \"value\" FROM \"cpu.percent|m\" WHERE \"node\" =~ /$node$/ AND  GROUP BY \"node\"",
                                "refId": "A",
                                "resultFormat": "time_series",
                                "select": [
                                    [
                                        {
                                            "params": [
                                                "value"
                                            ],
                                            "type": "field"
                                        }
                                    ]
                                ],
                                "tags": [
                                    {
                                        "key": "node",
                                        "operator": "=~",
                                        "value": "/$node$/"
                                    }
                                ]
                            }
                        ],
                        "title": "CPU",
                        "tooltip": {
                            "shared": True,
                            "value_type": "cumulative"
                        },
                        "type": "graph",
                        "x-axis": True,
                        "y-axis": True,
                        "y_formats": [
                            "short",
                            "short"
                        ]
                    },
                    {
                        "aliasColors": {},
                        "bars": False,
                        "datasource": "influxdb_main",
                        "editable": True,
                        "error": False,
                        "fill": 1,
                        "grid": {
                            "leftLogBase": 1,
                            "rightLogBase": 1,
                            "threshold1Color": "rgba(216, 200, 27, 0.27)",
                            "threshold2Color": "rgba(234, 112, 112, 0.22)"
                        },
                        "id": 2,
                        "isNew": True,
                        "legend": {
                            "avg": False,
                            "current": False,
                            "max": False,
                            "min": False,
                            "show": True,
                            "total": False,
                            "values": False
                        },
                        "lines": True,
                        "linewidth": 2,
                        "percentage": False,
                        "pointradius": 5,
                        "points": False,
                        "renderer": "flot",
                        "seriesOverrides": [],
                        "span": 12,
                        "stack": False,
                        "steppedLine": False,
                        "targets": [
                            {
                                "dsType": "influxdb",
                                "groupBy": [
                                    {
                                        "params": [
                                            "node"
                                        ],
                                        "type": "tag"
                                    }
                                ],
                                "measurement": "memory.virtual.used|m",
                                "query": "SELECT \"value\" FROM \"memory.virtual.used|m\" WHERE \"node\" =~ /$node$/ AND  GROUP BY \"node\"",
                                "refId": "A",
                                "resultFormat": "time_series",
                                "select": [
                                    [
                                        {
                                            "params": [
                                                "value"
                                            ],
                                            "type": "field"
                                        }
                                    ]
                                ],
                                "tags": [
                                    {
                                        "key": "node",
                                        "operator": "=~",
                                        "value": "/$node$/"
                                    }
                                ]
                            }
                        ],
                        "title": "Memory",
                        "tooltip": {
                            "shared": True,
                            "value_type": "cumulative"
                        },
                        "type": "graph",
                        "x-axis": True,
                        "y-axis": True,
                        "y_formats": [
                            "short",
                            "short"
                        ]
                    },
                    {
                        "aliasColors": {},
                        "bars": False,
                        "datasource": "influxdb_main",
                        "editable": True,
                        "error": False,
                        "fill": 1,
                        "grid": {
                            "leftLogBase": 1,
                            "rightLogBase": 1,
                            "threshold1Color": "rgba(216, 200, 27, 0.27)",
                            "threshold2Color": "rgba(234, 112, 112, 0.22)"
                        },
                        "id": 3,
                        "isNew": True,
                        "legend": {
                            "avg": False,
                            "current": False,
                            "max": False,
                            "min": False,
                            "show": True,
                            "total": False,
                            "values": False
                        },
                        "lines": True,
                        "linewidth": 2,
                        "percentage": False,
                        "pointradius": 5,
                        "points": False,
                        "renderer": "flot",
                        "seriesOverrides": [],
                        "span": 12,
                        "stack": False,
                        "steppedLine": False,
                        "targets": [
                            {
                                "dsType": "influxdb",
                                "groupBy": [
                                    {
                                        "params": [
                                            "node"
                                        ],
                                        "type": "tag"
                                    }
                                ],
                                "measurement": "/network\\.kbytes\\.recv\\|m|network\\.kbytes\\.sent\\|m/",
                                "query": "SELECT \"value\" FROM /network\\.kbytes\\.recv\\|m|network\\.kbytes\\.sent\\|m/ WHERE \"node\" =~ /$node$/ AND  GROUP BY \"node\"",
                                "refId": "A",
                                "resultFormat": "time_series",
                                "select": [
                                    [
                                        {
                                            "params": [
                                                "value"
                                            ],
                                            "type": "field"
                                        }
                                    ]
                                ],
                                "tags": [
                                    {
                                        "key": "node",
                                        "operator": "=~",
                                        "value": "/$node$/"
                                    }
                                ]
                            }
                        ],
                        "title": "Network",
                        "tooltip": {
                            "shared": True,
                            "value_type": "cumulative"
                        },
                        "type": "graph",
                        "x-axis": True,
                        "y-axis": True,
                        "y_formats": [
                            "short",
                            "short"
                        ]
                    }
                ],
                "title": "Row"
            }
        ],
        "time": {
            "from": "2016-04-04T01:13:22.824Z",
            "to": "2016-04-04T13:13:22.826Z"
        },
        "timepicker": {
            "refresh_intervals": [
                "5s",
                "10s",
                "30s",
                "1m",
                "5m",
                "15m",
                "30m",
                "1h",
                "2h",
                "1d"
            ],
            "time_options": [
                "5m",
                "15m",
                "1h",
                "6h",
                "12h",
                "24h",
                "2d",
                "7d",
                "30d"
            ]
        },
        "templating": {
            "list": [
                {
                    "allFormat": "pipe",
                    "current": {
                        "tags": [],
                        "text": "All",
                        "value": "grafana_1"
                    },
                    "datasource": "influxdb_main",
                    "includeAll": True,
                    "multi": True,
                    "multiFormat": "pipe",
                    "name": "node",
                    "options": [
                        {
                            "selected": True,
                            "text": "All",
                            "value": "grafana_1"
                        },
                        {
                            "selected": False,
                            "text": "grafana_1",
                            "value": "grafana_1"
                        }
                    ],
                    "query": "SHOW TAG VALUES WITH KEY = \"node\"",
                    "refresh": False,
                    "regex": "",
                    "type": "query"
                }
            ]
        },
        "annotations": {
            "list": []
        },
        "refresh": False,
        "schemaVersion": 8,
        "version": 1,
        "links": []
    },
    "overwrite": False
}