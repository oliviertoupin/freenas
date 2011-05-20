import rrdtool, os, re, hashlib

# Interface statistics
rrd_dir = "/var/db/collectd/rrd/localhost/interface"

rrds = []
for file in os.listdir(rrd_dir):
    if file.startswith("."):
        continue
    try:
        octets = re.search(r'(?<=octets-)[a-z0-9]+', file)
    except AttributeError:
        os.remove(os.path.join(rrd_dir, file))
        continue
    if octets:
        filename_md5 = "." + file
        old_md5 = None
        if os.path.exists(os.path.join(rrd_dir, filename_md5)):
            fh = open(os.path.join(rrd_dir, filename_md5), "r")
            old_md5 = fh.read()
            fh.close()
        current_md5 = hashlib.md5()
        fh = open(os.path.join(rrd_dir, file), "r")
        cur_md5 = fh.read()
        current_md5.update(cur_md5)
        fh.close()
        new_md5 = current_md5.hexdigest()
        if new_md5 == old_md5:
            os.remove(os.path.join(rrd_dir, file))
            os.remove(os.path.join(rrd_dir, filename_md5))
        else:
            fh = open(os.path.join(rrd_dir, filename_md5), "w")
            fh.write(new_md5)
            fh.close()
            rrds.append((file, octets.group(0)))

for (file, iface) in rrds:
    times = ['1h', '1d', '1w', '1m', '1y']
    for time in times:
        rrdtool.graph("/tmp/if-%s-%s.png" % (iface, time),
                      '--imgformat', 'PNG',
                      '--vertical-label', 'Bits per second',
                      '--title', 'Interface Traffic (%s)' % iface,
                      '--lower-limit', '0',
                      '--end', 'now',
                      '--start', 'end-%s' % time,
                      'DEF:min_rx_raw=%s:rx:MIN' % os.path.join(rrd_dir, file),
                      'DEF:avg_rx_raw=%s:rx:AVERAGE' % os.path.join(rrd_dir, file),
                      'DEF:max_rx_raw=%s:rx:MAX' % os.path.join(rrd_dir, file),
                      'DEF:min_tx_raw=%s:tx:MIN' % os.path.join(rrd_dir, file),
                      'DEF:avg_tx_raw=%s:tx:AVERAGE' % os.path.join(rrd_dir, file),
                      'DEF:max_tx_raw=%s:tx:MAX' % os.path.join(rrd_dir, file),
                      'CDEF:min_rx=min_rx_raw,8,*',
                      'CDEF:avg_rx=avg_rx_raw,8,*',
                      'CDEF:max_rx=max_rx_raw,8,*',
                      'CDEF:min_tx=min_tx_raw,8,*',
                      'CDEF:avg_tx=avg_tx_raw,8,*',
                      'CDEF:max_tx=max_tx_raw,8,*',
                      'CDEF:avg_rx_bytes=avg_rx,8,/',
                      'VDEF:global_min_rx=min_rx,MINIMUM',
                      'VDEF:global_avg_rx=avg_rx,AVERAGE',
                      'VDEF:global_max_rx=max_rx,MAXIMUM',
                      'VDEF:global_tot_rx=avg_rx_bytes,TOTAL',
                      'CDEF:avg_tx_bytes=avg_tx,8,/',
                      'VDEF:global_min_tx=min_tx,MINIMUM',
                      'VDEF:global_avg_tx=avg_tx,AVERAGE',
                      'VDEF:global_max_tx=max_tx,MAXIMUM',
                      'VDEF:global_tot_tx=avg_tx_bytes,TOTAL',
                      'CDEF:overlap=avg_rx,avg_tx,LT,avg_rx,avg_tx,IF',
                      'AREA:avg_rx#bfbfff',
                      'AREA:avg_tx#bfe0cf',
                      'LINE1:avg_rx#0000ff:RX',
                      'GPRINT:global_min_rx:%5.1lf%s Min,',
                      'GPRINT:global_avg_rx:%5.1lf%s Avg,',
                      'GPRINT:global_max_rx:%5.1lf%s Max,',
                      'GPRINT:global_tot_rx:ca. %5.1lf%s Total\l',
                      'LINE1:avg_tx#00b000:TX',
                      'GPRINT:global_min_tx:%5.1lf%s Min,',
                      'GPRINT:global_avg_tx:%5.1lf%s Avg,',
                      'GPRINT:global_max_tx:%5.1lf%s Max,',
                      'GPRINT:global_tot_tx:ca. %5.1lf%s Total\l'
                      )

# CPU usage stats
cpu_idle = "/var/db/collectd/rrd/localhost/cpu-0/cpu-idle.rrd"
cpu_nice = "/var/db/collectd/rrd/localhost/cpu-0/cpu-nice.rrd"
cpu_user = "/var/db/collectd/rrd/localhost/cpu-0/cpu-user.rrd"
cpu_system = "/var/db/collectd/rrd/localhost/cpu-0/cpu-system.rrd"
cpu_interrupt = "/var/db/collectd/rrd/localhost/cpu-0/cpu-interrupt.rrd"
file = "cpu"
times = ['1h', '1d', '1w', '1m', '1y']
for time in times:
    rrdtool.graph("/tmp/%s-%s.png" % (file, time),
              '--imgformat', 'PNG',
              '--vertical-label', '%CPU',
              '--title', 'CPU Usage',
              '--lower-limit', '0',
              '--end', 'now',
              '--start', 'end-%s' % time,
              'DEF:min0=%s:value:MIN' % cpu_idle,
              'DEF:avg0=%s:value:AVERAGE' % cpu_idle,
              'DEF:max0=%s:value:MAX' % cpu_idle,
              'DEF:min1=%s:value:MIN' % cpu_nice,
              'DEF:avg1=%s:value:AVERAGE' % cpu_nice,
              'DEF:max1=%s:value:MAX' % cpu_nice,
              'DEF:min2=%s:value:MIN' % cpu_user,
              'DEF:avg2=%s:value:AVERAGE' % cpu_user,
              'DEF:max2=%s:value:MAX' % cpu_user,
              'DEF:min3=%s:value:MIN' % cpu_system,
              'DEF:avg3=%s:value:AVERAGE' % cpu_system,
              'DEF:max3=%s:value:MAX' % cpu_system,
              'DEF:min4=%s:value:MIN' % cpu_interrupt,
              'DEF:avg4=%s:value:AVERAGE' % cpu_interrupt,
              'DEF:max4=%s:value:MAX' % cpu_interrupt,
              'CDEF:cdef4=avg4,UN,0,avg4,IF',
              'CDEF:cdef3=avg3,UN,0,avg3,IF,cdef4,+',
              'CDEF:cdef2=avg2,UN,0,avg2,IF,cdef3,+',
              'CDEF:cdef1=avg1,UN,0,avg1,IF,cdef2,+',
              'CDEF:cdef0=avg0,UN,0,avg0,IF,cdef1,+',
              'AREA:cdef0#f9f9f9',
              'AREA:cdef1#bff7bf',
              'AREA:cdef2#bfbfff',
              'AREA:cdef3#ffbfbf',
              'AREA:cdef4#e7bfe7',
              'LINE1:cdef0#e8e8e8:Idle  ',
              'GPRINT:min0:MIN:%5.2lf Min,',
              'GPRINT:avg0:AVERAGE:%5.2lf Avg,',
              'GPRINT:max0:MAX:%5.2lf Max,',
              'GPRINT:avg0:LAST:%5.2lf Last\l',
              'LINE1:cdef1#00e000:Nice  ',
              'GPRINT:min1:MIN:%5.2lf Min,',
              'GPRINT:avg1:AVERAGE:%5.2lf Avg,',
              'GPRINT:max1:MAX:%5.2lf Max,',
              'GPRINT:avg1:LAST:%5.2lf Last\l',
              'LINE1:cdef2#0000ff:User  ',
              'GPRINT:min2:MIN:%5.2lf Min,',
              'GPRINT:avg2:AVERAGE:%5.2lf Avg,',
              'GPRINT:max2:MAX:%5.2lf Max,',
              'GPRINT:avg2:LAST:%5.2lf Last\l',
              'LINE1:cdef3#ff0000:System',
              'GPRINT:min3:MIN:%5.2lf Min,',
              'GPRINT:avg3:AVERAGE:%5.2lf Avg,',
              'GPRINT:max3:MAX:%5.2lf Max,',
              'GPRINT:avg3:LAST:%5.2lf Last\l',
              'LINE1:cdef4#a000a0:IRQ   ',
              'GPRINT:min4:MIN:%5.2lf Min,',
              'GPRINT:avg4:AVERAGE:%5.2lf Avg,',
              'GPRINT:max4:MAX:%5.2lf Max,',
              'GPRINT:avg4:LAST:%5.2lf Last\l'
              )

# Memory usage stats
memory_free = "/var/db/collectd/rrd/localhost/memory/memory-free.rrd"
memory_active = "/var/db/collectd/rrd/localhost/memory/memory-active.rrd"
memory_cache = "/var/db/collectd/rrd/localhost/memory/memory-cache.rrd"
memory_inactive = "/var/db/collectd/rrd/localhost/memory/memory-inactive.rrd"
memory_wired = "/var/db/collectd/rrd/localhost/memory/memory-wired.rrd"
file = "memory"
times = ['1h', '1d', '1w', '1m', '1y']
for time in times:
    rrdtool.graph("/tmp/%s-%s.png" % (file, time),
              '--imgformat', 'PNG',
              '--vertical-label', 'Bytes',
              '--title', 'Physical memory utilization',
              '--lower-limit', '0',
              '--end', 'now',
              '--start', 'end-%s' % time,
              '-b', '1024',
              'DEF:min0=%s:value:MIN' % memory_free,
              'DEF:avg0=%s:value:AVERAGE' % memory_free,
              'DEF:max0=%s:value:MAX' % memory_free,
              'DEF:min1=%s:value:MIN' % memory_active,
              'DEF:avg1=%s:value:AVERAGE' % memory_active,
              'DEF:max1=%s:value:MAX' % memory_active,
              'DEF:min2=%s:value:MIN' % memory_cache,
              'DEF:avg2=%s:value:AVERAGE' % memory_cache,
              'DEF:max2=%s:value:MAX' % memory_cache,
              'DEF:min3=%s:value:MIN' % memory_inactive,
              'DEF:avg3=%s:value:AVERAGE' % memory_inactive,
              'DEF:max3=%s:value:MAX' % memory_inactive,
              'DEF:min4=%s:value:MIN' % memory_wired,
              'DEF:avg4=%s:value:AVERAGE' % memory_wired,
              'DEF:max4=%s:value:MAX' % memory_wired,
              'CDEF:cdef4=avg4,UN,0,avg4,IF',
              'CDEF:cdef3=avg3,UN,0,avg3,IF,cdef4,+',
              'CDEF:cdef2=avg2,UN,0,avg2,IF,cdef3,+',
              'CDEF:cdef1=avg1,UN,0,avg1,IF,cdef2,+',
              'CDEF:cdef0=avg0,UN,0,avg0,IF,cdef1,+',
              'AREA:cdef0#bff7bf',
              'AREA:cdef1#bfbfbf',
              'AREA:cdef2#bfbfbf',
              'AREA:cdef3#bfbfbf',
              'AREA:cdef4#bfbfbf',
              'LINE1:cdef0#00e000:Free    ',
              'GPRINT:min0:MIN:%5.1lf%s Min,',
              'GPRINT:avg0:AVERAGE:%5.1lf%s Avg,',
              'GPRINT:max0:MAX:%5.1lf%s Max,',
              'GPRINT:avg0:LAST:%5.1lf%s Last\l',
              'LINE1:cdef1#0b0b61:active  ',
              'GPRINT:min1:MIN:%5.1lf%s Min,',
              'GPRINT:avg1:AVERAGE:%5.1lf%s Avg,',
              'GPRINT:max1:MAX:%5.1lf%s Max,',
              'GPRINT:avg1:LAST:%5.1lf%s Last\l',
              'LINE1:cdef2#08808a:cache   ',
              'GPRINT:min2:MIN:%5.1lf%s Min,',
              'GPRINT:avg2:AVERAGE:%5.1lf%s Avg,',
              'GPRINT:max2:MAX:%5.1lf%s Max,',
              'GPRINT:avg2:LAST:%5.1lf%s Last\l',
              'LINE1:cdef3#0404b4:inactive',
              'GPRINT:min3:MIN:%5.1lf%s Min,',
              'GPRINT:avg3:AVERAGE:%5.1lf%s Avg,',
              'GPRINT:max3:MAX:%5.1lf%s Max,',
              'GPRINT:avg3:LAST:%5.1lf%s Last\l',
              'LINE1:cdef4#0101df:wired   ',
              'GPRINT:min4:MIN:%5.1lf%s Min,',
              'GPRINT:avg4:AVERAGE:%5.1lf%s Avg,',
              'GPRINT:max4:MAX:%5.1lf%s Max,',
              'GPRINT:avg4:LAST:%5.1lf%s Last\l'
              )

# System Load stats
load = "/var/db/collectd/rrd/localhost/load/load.rrd"
file = "load"
times = ['1h', '1d', '1w', '1m', '1y']
for time in times:
    rrdtool.graph("/tmp/%s-%s.png" % (file, time),
              '--imgformat', 'PNG',
              '--vertical-label', 'System Load',
              '--title', 'System Load',
              '--lower-limit', '0',
              '--end', 'now',
              '--start', 'end-%s' % time,
              'DEF:s_min=%s:shortterm:MIN' % load,
              'DEF:s_avg=%s:shortterm:AVERAGE' % load,
              'DEF:s_max=%s:shortterm:MAX' % load,
              'DEF:m_min=%s:midterm:MIN' % load,
              'DEF:m_avg=%s:midterm:AVERAGE' % load,
              'DEF:m_max=%s:midterm:MAX' % load,
              'DEF:l_min=%s:longterm:MIN' % load,
              'DEF:l_avg=%s:longterm:AVERAGE' % load,
              'DEF:l_max=%s:longterm:MAX' % load,
              'AREA:s_max#bfffbf',
              'AREA:s_min#FFFFFF',
              'LINE1:s_avg#00ff00: 1 min',
              'GPRINT:s_min:MIN:%.2lf Min,',
              'GPRINT:s_avg:AVERAGE:%.2lf Avg,',
              'GPRINT:s_max:MAX:%.2lf Max,',
              'GPRINT:s_avg:LAST:%.2lf Last\l',
              'LINE1:m_avg#0000ff: 5 min',
              'GPRINT:m_min:MIN:%.2lf Min,',
              'GPRINT:m_avg:AVERAGE:%.2lf Avg,',
              'GPRINT:m_max:MAX:%.2lf Max,',
              'GPRINT:m_avg:LAST:%.2lf Last\l',
              'LINE1:l_avg#ff0000:15 min',
              'GPRINT:l_min:MIN:%.2lf Min,',
              'GPRINT:l_avg:AVERAGE:%.2lf Avg,',
              'GPRINT:l_max:MAX:%.2lf Max,',
              'GPRINT:l_avg:LAST:%.2lf Last\l'
              )

# Processes
blocked = "/var/db/collectd/rrd/localhost/processes/ps_state-blocked.rrd"
zombies = "/var/db/collectd/rrd/localhost/processes/ps_state-zombies.rrd"
stopped = "/var/db/collectd/rrd/localhost/processes/ps_state-stopped.rrd"
running = "/var/db/collectd/rrd/localhost/processes/ps_state-running.rrd"
sleeping = "/var/db/collectd/rrd/localhost/processes/ps_state-sleeping.rrd"
idle = "/var/db/collectd/rrd/localhost/processes/ps_state-idle.rrd"
wait = "/var/db/collectd/rrd/localhost/processes/ps_state-wait.rrd"
file = "processes"
times = ['1h', '1d', '1w', '1m', '1y']
for time in times:
    rrdtool.graph("/tmp/%s-%s.png" % (file, time),
              '--imgformat', 'PNG',
              '--vertical-label', 'Processes',
              '--title', 'Processes',
              '--lower-limit', '0',
              '--end', 'now',
              '--start', 'end-%s' % time,
              'DEF:min0=%s:value:MIN' % blocked,
              'DEF:avg0=%s:value:AVERAGE' % blocked,
              'DEF:max0=%s:value:MAX' % blocked,
              'DEF:min1=%s:value:MIN' % zombies,
              'DEF:avg1=%s:value:AVERAGE' % zombies,
              'DEF:max1=%s:value:MAX' % zombies,
              'DEF:min2=%s:value:MIN' % stopped,
              'DEF:avg2=%s:value:AVERAGE' % stopped,
              'DEF:max2=%s:value:MAX' % stopped,
              'DEF:min3=%s:value:MIN' % running,
              'DEF:avg3=%s:value:AVERAGE' % running,
              'DEF:max3=%s:value:MAX' % running,
              'DEF:min4=%s:value:MIN' % sleeping,
              'DEF:avg4=%s:value:AVERAGE' % sleeping,
              'DEF:max4=%s:value:MAX' % sleeping,
              'DEF:min5=%s:value:MIN' % idle,
              'DEF:avg5=%s:value:AVERAGE' % idle,
              'DEF:max5=%s:value:MAX' % idle,
              'DEF:min6=%s:value:MIN' % wait,
              'DEF:avg6=%s:value:AVERAGE' % wait,
              'DEF:max6=%s:value:MAX' % wait,
              'CDEF:cdef6=avg6,UN,0,avg6,IF',
              'CDEF:cdef5=avg5,UN,0,avg5,IF,cdef6,+',
              'CDEF:cdef4=avg4,UN,0,avg4,IF,cdef5,+',
              'CDEF:cdef3=avg3,UN,0,avg3,IF,cdef4,+',
              'CDEF:cdef2=avg2,UN,0,avg2,IF,cdef3,+',
              'CDEF:cdef1=avg1,UN,0,avg1,IF,cdef2,+',
              'CDEF:cdef0=avg0,UN,0,avg0,IF,cdef1,+',
              'AREA:cdef0#ffbfff',
              'AREA:cdef1#ffbfbf',
              'AREA:cdef2#e7bfe7',
              'AREA:cdef3#bff7bf',
              'AREA:cdef4#bfbfff',
              'AREA:cdef5#bfbfbf',
              'AREA:cdef6#bfbfbf',
              'LINE1:cdef0#ff00ff:Blocked ',
              'GPRINT:min0:MIN:%5.1lf Min,',
              'GPRINT:avg0:AVERAGE:%5.1lf Avg,',
              'GPRINT:max0:MAX:%5.1lf Max,',
              'GPRINT:avg0:LAST:%5.1lf Last\l',
              'LINE1:cdef1#ff0000:Zombies ',
              'GPRINT:min1:MIN:%5.1lf Min,',
              'GPRINT:avg1:AVERAGE:%5.1lf Avg,',
              'GPRINT:max1:MAX:%5.1lf Max,',
              'GPRINT:avg1:LAST:%5.1lf Last\l',
              'LINE1:cdef2#a000a0:Stopped ',
              'GPRINT:min2:MIN:%5.1lf Min,',
              'GPRINT:avg2:AVERAGE:%5.1lf Avg,',
              'GPRINT:max2:MAX:%5.1lf Max,',
              'GPRINT:avg2:LAST:%5.1lf Last\l',
              'LINE1:cdef3#00e000:Running ',
              'GPRINT:min3:MIN:%5.1lf Min,',
              'GPRINT:avg3:AVERAGE:%5.1lf Avg,',
              'GPRINT:max3:MAX:%5.1lf Max,',
              'GPRINT:avg3:LAST:%5.1lf Last\l',
              'LINE1:cdef4#0000ff:Sleeping',
              'GPRINT:min4:MIN:%5.1lf Min,',
              'GPRINT:avg4:AVERAGE:%5.1lf Avg,',
              'GPRINT:max4:MAX:%5.1lf Max,',
              'GPRINT:avg4:LAST:%5.1lf Last\l',
              'LINE1:cdef5#000000:idle    ',
              'GPRINT:min5:MIN:%5.1lf Min,',
              'GPRINT:avg5:AVERAGE:%5.1lf Avg,',
              'GPRINT:max5:MAX:%5.1lf Max,',
              'GPRINT:avg5:LAST:%5.1lf Last\l',
              'LINE1:cdef6#000000:wait    ',
              'GPRINT:min6:MIN:%5.1lf Min,',
              'GPRINT:avg6:AVERAGE:%5.1lf Avg,',
              'GPRINT:max6:MAX:%5.1lf Max,',
              'GPRINT:avg6:LAST:%5.1lf Last\l'
              )

free = "/var/db/collectd/rrd/localhost/swap/swap-free.rrd"
used = "/var/db/collectd/rrd/localhost/swap/swap-used.rrd"
file = "swap"
times = ['1h', '1d', '1w', '1m', '1y']
for time in times:
    rrdtool.graph("/tmp/%s-%s.png" % (file, time),
              '--imgformat', 'PNG',
              '--vertical-label', 'Bytes',
              '--title', 'Swap Utilization',
              '--lower-limit', '0',
              '--end', 'now',
              '--start', 'end-%s' % time,
              'DEF:min0=%s:value:MIN' % free,
              'DEF:avg0=%s:value:AVERAGE' % free,
              'DEF:max0=%s:value:MAX' % free,
              'DEF:min1=%s:value:MIN' % used,
              'DEF:avg1=%s:value:AVERAGE' % used,
              'DEF:max1=%s:value:MAX' % used,
              'CDEF:cdef1=avg1,UN,0,avg1,IF',
              'CDEF:cdef0=avg0,UN,0,avg0,IF,cdef1,+',
              'AREA:cdef0#bff7bf',
              'AREA:cdef1#ffbfbf',
              'LINE1:cdef0#00e000:Free    ',
              'GPRINT:min0:MIN:%5.1lf%s Min,',
              'GPRINT:avg0:AVERAGE:%5.1lf%s Avg,',
              'GPRINT:max0:MAX:%5.1lf%s Max,',
              'GPRINT:avg0:LAST:%5.1lf%s Last\l',
              'LINE1:cdef1#ff0000:Used    ',
              'GPRINT:min1:MIN:%5.1lf%s Min,',
              'GPRINT:avg1:AVERAGE:%5.1lf%s Avg,',
              'GPRINT:max1:MAX:%5.1lf%s Max,',
              'GPRINT:avg1:LAST:%5.1lf%s Last\l'
              )

# diskspace statistics
rrd_dir = "/var/db/collectd/rrd/localhost/df"
if os.path.isdir(rrd_dir):
    for file in os.listdir(rrd_dir):
        if file.startswith("."):
            continue
        try:
            volname = re.search(r'(?<=df-mnt-)(.*)\.rrd', file).group(1)
        except AttributeError:
            os.remove(os.path.join(rrd_dir, file))
            continue
        filename_md5 = "." + file
        old_md5 = None
        if os.path.exists(os.path.join(rrd_dir, filename_md5)):
            fh = open(os.path.join(rrd_dir, filename_md5), "r")
            old_md5 = fh.read()
            fh.close()
        current_md5 = hashlib.md5()
        fh = open(os.path.join(rrd_dir, file), "r")
        cur_md5 = fh.read()
        current_md5.update(cur_md5)
        fh.close()
        new_md5 = current_md5.hexdigest()
        if new_md5 == old_md5:
            os.remove(os.path.join(rrd_dir, file))
            os.remove(os.path.join(rrd_dir, filename_md5))
            continue
        else:
            fh = open(os.path.join(rrd_dir, filename_md5), "w")
            fh.write(new_md5)
            fh.close()
        times = ['1h', '1d', '1w', '1m', '1y']
        for time in times:
            rrdtool.graph("/tmp/df-%s-%s.png" % (volname, time),
                          '--imgformat', 'PNG',
                          '--vertical-label', 'Bytes',
                          '--title', 'Diskspace (%s)' % volname,
                          '--lower-limit', '0',
                          '--end', 'now',
                          '--start', 'end-%s' % time,
                          'DEF:free_min=%s:free:MIN' % os.path.join(rrd_dir, file),
                          'DEF:free_avg=%s:free:AVERAGE' % os.path.join(rrd_dir, file),
                          'DEF:free_max=%s:free:MAX' % os.path.join(rrd_dir, file),
                          'DEF:used_min=%s:used:MIN' % os.path.join(rrd_dir, file),
                          'DEF:used_avg=%s:used:AVERAGE' % os.path.join(rrd_dir, file),
                          'DEF:used_max=%s:used:MAX' % os.path.join(rrd_dir, file),
                          'CDEF:both_avg=free_avg,used_avg,+',
                          'AREA:both_avg#bfffbf',
                          'AREA:used_avg#ffbfbf',
                          'LINE1:both_avg#00ff00:Free',
                          'GPRINT:free_min:MIN:%5.1lf%sB Min,',
                          'GPRINT:free_avg:AVERAGE:%5.1lf%sB Avg,',
                          'GPRINT:free_max:MAX:%5.1lf%sB Max,',
                          'GPRINT:free_avg:LAST:%5.1lf%sB Last\l',
                          'LINE1:used_avg#ff0000:Used',
                          'GPRINT:used_min:MIN:%5.1lf%sB Min,',
                          'GPRINT:used_avg:AVERAGE:%5.1lf%sB Avg,',
                          'GPRINT:used_max:MAX:%5.1lf%sB Max,',
                          'GPRINT:used_avg:LAST:%5.1lf%sB Last\l'
                          )
if not os.path.isdir("/var/db/graphs"):
    os.mkdir("/var/db/graphs")
graphdir = ['hourly', 'daily', 'weekly', 'monthly', 'yearly']
for period in graphdir:
    if not os.path.isdir(os.path.join("/var/db/graphs", period)):
        os.mkdir(os.path.join("/var/db/graphs", period))

os.system("find /var/db/graphs -type f -delete")
for file in os.listdir("/tmp/"):
    if "1h.png" in file:
        os.system("cp /tmp/%s /var/db/graphs/hourly/" % file)
    elif "1d.png" in file:
        os.system("cp /tmp/%s /var/db/graphs/daily/" % file)
    elif "1w.png" in file:
        os.system("cp /tmp/%s /var/db/graphs/weekly/" % file)
    elif "1m.png" in file:
        os.system("cp /tmp/%s /var/db/graphs/monthly/" % file)
    elif "1y.png" in file:
        os.system("cp /tmp/%s /var/db/graphs/yearly/" % file)
    else:
        pass
