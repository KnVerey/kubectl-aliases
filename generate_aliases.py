#!/usr/bin/env python2

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools
import sys
import os.path

def main():
    # (alias, full, restrict_to_aliases, incompatible_with)

    cmds=[
        ('kg','kubectl get', None, None),
        ('kd','kubectl describe', None, None),
    ]

    res=[
        ('po','pods', ['kd'], None),
        ('po',"pods -o=custom-columns-file=$KUBECTL_CUSTOM_COLUMNS_DIR/pod-columns.txt", ['kg'], None),
        ('dep','deployment', ['kg','kd'], None),  # does not match official short name
        ('svc','service', ['kg','kd'], None),
        ('ing','ingress', ['kg','kd'], None),
        ('cm','configmap', ['kg','kd'], None),
        ('sec','secret', ['kg','kd'], None), # does not match official short name
        ('no','nodes',['kg','kd'], None),
        ('ns','namespaces',['kg','kd'], None),
        ('crd','customresourcedefinitions', ['kg','kd'], None),
        ('tpr','thirdpartyresources', ['kg','kd'], None), # does not match official short name
        ('ds','daemonsets', ['kg','kd'], None),
        ('cron','cronjobs', ['kg','kd'], None), # does not match official short name
        ('ep','endpoints', ['kg','kd'], None),
        ('ev','events', ['kg','kd'], None),
        ('hpa','horizontalpodautoscalers', ['kg','kd'], None),
        ('lr','limitranges', ['kg','kd'], None), # does not match official short name
        ('job','jobs', ['kg','kd'], None),
        ('pvc','persistentvolumeclaims', ['kg','kd'], None),
        ('pv','persistentvolumes', ['kg','kd'], None),
        ('pdb','poddisruptionbudgets', ['kg','kd'], None),
        ('rs','replicasets', ['kg','kd'], None),
        ('qta','resourcequotas', ['kg','kd'], None), # does not match official short name
        ('sa','serviceaccounts', ['kg','kd'], None),
        ('ss','statefulsets', ['kg','kd'], None),  # does not match official short name
        ('stor','storageclasses', ['kg','kd'], None),  # does not match official short name
        # CUSTOM RESOURCES
        ('redis',"redises -o=custom-columns-file=$KUBECTL_CUSTOM_COLUMNS_DIR/redis-columns.txt", ['kg'], None),
        ('redis',"redises", ['kd'], None),
        ('sql',"cloudsql -o=custom-columns-file=$KUBECTL_CUSTOM_COLUMNS_DIR/cloudsql-columns.txt", ['kg'], None),
        ('sql',"cloudsql", ['kd'], None),
        ('bugs',"bugsnags -o=custom-columns-file=$KUBECTL_CUSTOM_COLUMNS_DIR/bugsnag-columns.txt", ['kg'], None),
        ('bugs','bugsnags', ['kd'], None),
        ('es',"elasticsearches -o=custom-columns-file=$KUBECTL_CUSTOM_COLUMNS_DIR/elasticsearch-columns.txt", ['kg'], None),
        ('es','elasticsearches', ['kd'], None),
        ('memd',"memcacheds -o=custom-columns-file=$KUBECTL_CUSTOM_COLUMNS_DIR/memcached-columns.txt", ['kg'], None),
        ('memd','memcacheds', ['kd'], None),
        ('state',"statefulservices -o=custom-columns-file=$KUBECTL_CUSTOM_COLUMNS_DIR/statefulservice-columns.txt", ['kg'], None),
        ('state','statefulservices', ['kd'], None),
        ('topic',"topics -o=custom-columns-file=$KUBECTL_CUSTOM_COLUMNS_DIR/topic-columns.txt", ['kg'], None),
        ('topic','topics', ['kd'], None),
    ]

    args=[
        # ('oyaml','-o=yaml', ['kg'], ['owide','ojson']),
        # ('owide','-o=wide', ['kg'], ['oyaml','ojson']),
        # ('ojson','-o=json', ['kg'], ['owide','oyaml']),
        ('all', '--all-namespaces', ['kg'], ['no','stor','pv','ns']),
        # ('w', '--watch', ['kg'], ['oyaml','ojson']),
    ]

    # [(part, optional, take_exactly_one)]
    parts=[
        (cmds, False, True),
        (res, False, True),
        (args, True, False),
    ]

    out = gen(cmds, parts)
    out = filter(is_valid, out)

    # prepare output
    if not sys.stdout.isatty():
        header_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'license_header')
        with open(header_path, 'r') as f: print f.read()
    for cmd in cmds:
        print "alias {}='{}'".format(cmd[0], cmd[1])
    for cmd in out:
        print "alias {}='{}'".format(
            ''.join([a[0] for a in cmd]),
            ' '.join([a[1] for a in cmd])
        )

def gen(cmds, parts):
    out = [()]
    for (items, optional, take_exactly_one) in parts:
        orig=list(out)
        combos = []

        if optional and take_exactly_one: combos=combos.append([])

        if take_exactly_one: combos = combinations(items, 1, include_0=optional)
        else: combos = combinations(items, len(items), include_0=optional)

        # permutate the combinations if optional (args are not positional)
        if optional:
            new_combos = []
            for c in combos:
                new_combos += list(itertools.permutations(c))
            combos = new_combos

        new_out=[]
        for segment in combos:
            for stuff in orig:
                new_out.append(stuff+segment)
        out=new_out
    return out

def is_valid(cmd):
    for i in xrange(0, len(cmd)):
        # check at least one of requirements are in the cmd
        requirements=cmd[i][2]
        if requirements:
            found=False
            for r in requirements:
                for j in xrange(0, i):
                    if cmd[j][0] == r:
                        found=True
                        break
                if found:
                    break
            if not found:
                return False

        # check none of the incompatibilities are in the cmd
        incompatibilities=cmd[i][3]
        if incompatibilities:
            found=False
            for inc in incompatibilities:
                for j in xrange(0, i):
                    if cmd[j][0] == inc:
                        found=True
                        break
                if found:
                    break
            if found:
                return False

    return True

def combinations(a, n, include_0=True):
    l = []
    for j in xrange(0, n+1):
        if not include_0 and j == 0: continue
        l += list(itertools.combinations(a, j))
    return l

if __name__=='__main__':
    main()
