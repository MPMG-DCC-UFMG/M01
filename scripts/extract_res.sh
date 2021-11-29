
dat=$1

for pref in "" "merged_"; do cat data/datasets/$dat/"$pref"eval* | grep macro | awk "NR % 2 == 1" | scripts/avg_ci.py 2; done > /tmp/1
for pref in "" "merged_"; do cat data/datasets/$dat/"$pref"eval* | grep macro | awk "NR % 2 == 1" | scripts/avg_ci.py 3; done > /tmp/2
for pref in "" "merged_"; do cat data/datasets/$dat/"$pref"eval* | grep macro | awk "NR % 2 == 1" | scripts/avg_ci.py 4; done > /tmp/3

for pref in "" "merged_"; do cat data/datasets/$dat/"$pref"eval* | grep macro | awk "NR % 2 == 0" | scripts/avg_ci.py 2; done > /tmp/4
for pref in "" "merged_"; do cat data/datasets/$dat/"$pref"eval* | grep macro | awk "NR % 2 == 0" | scripts/avg_ci.py 3; done > /tmp/5
for pref in "" "merged_"; do cat data/datasets/$dat/"$pref"eval* | grep macro | awk "NR % 2 == 0" | scripts/avg_ci.py 4; done > /tmp/6


paste /tmp/1 /tmp/2 /tmp/3 /tmp/4 /tmp/5 /tmp/6


