# Mantém só as permissões do Health Connect que o Evolute realmente usa (leitura de treinos e batimentos).
# O plugin declara ~45 permissões (inclusive de escrita, glicose, pressão...). As demais são removidas na mescla do manifesto.
import re, sys
p = sys.argv[1]
s = open(p, encoding='utf8').read()
KEEP = {'READ_EXERCISE', 'READ_HEART_RATE', 'READ_DISTANCE', 'READ_ACTIVE_CALORIES_BURNED', 'READ_TOTAL_CALORIES_BURNED', 'READ_STEPS', 'READ_SLEEP', 'READ_RESTING_HEART_RATE'}
ALL = ['STEPS','DISTANCE','ACTIVE_CALORIES_BURNED','HEART_RATE','WEIGHT','SLEEP','RESPIRATORY_RATE','OXYGEN_SATURATION','RESTING_HEART_RATE','HEART_RATE_VARIABILITY','VO2_MAX','BLOOD_PRESSURE','BLOOD_GLUCOSE','BODY_TEMPERATURE','HEIGHT','FLOORS_CLIMBED','BODY_FAT','BASAL_BODY_TEMPERATURE','BASAL_METABOLIC_RATE','TOTAL_CALORIES_BURNED','MINDFULNESS','HYDRATION','NUTRITION','EXERCISE']
rm = []
for a in ALL:
    for mode in ('READ', 'WRITE'):
        n = mode + '_' + a
        if n not in KEEP:
            rm.append('    <uses-permission android:name="android.permission.health.%s" tools:node="remove" />' % n)
if 'xmlns:tools' not in s:
    s = s.replace('<manifest ', '<manifest xmlns:tools="http://schemas.android.com/tools" ', 1)
s = s.replace('</manifest>', '\n'.join(rm) + '\n</manifest>', 1)
open(p, 'w', encoding='utf8').write(s)
print('ok: removidas', len(rm), 'permissões')
