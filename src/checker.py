#!/usr/bin/env python
import re
import os
import sys
import math
import yaml
import json
import time
import pandas as pd
from tld import get_tld
from Levenshtein import distance
from confusables import unconfuse
from datetime import datetime, timedelta

suspicious_yaml = sys.argv[1]

with open(suspicious_yaml, "r") as f:
    suspicious = yaml.safe_load(f)

exclusions = [re.compile(exc, re.IGNORECASE) for exc in suspicious["exclusions"]]
regex = [
    {"score": exc["score"], "pattern": re.compile(exc["pattern"], re.IGNORECASE)}
    for exc in suspicious.get("regex", [])
]

def entropy(string):
    # 文字列の情報量を計算します
    prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
    entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
    return entropy


def score_domain(domain):
    """Score `domain`

    最も高いスコア、最も可能性の高いdomainはフィッシング サイト。

    引数
        domain (str): チェックするドメイン。

    戻り値：
        int: ドメインのスコア。
    """
    score = 0

    # 除外リストにマッチしたらスコア0
    for exclusion in exclusions:
        if exclusion.search(domain):
            return 0

    # 正規表現にマッチしたらスコアを加算する
    for r in regex:
        if r["pattern"].search(domain):
            score += r["score"]

    # ブランディングが低いTLD
    for t in suspicious["tlds"]:
        if domain.endswith(t):
            score += 20

    # 証明書のワイルドカード部分を削除
    if domain.startswith("*."):
        domain = domain[2:]

    # サブドメインの内部 TLD をキャッチするために TLD を削除 (ie. paypal.com.domain.com)
    try:
        res = get_tld(domain, as_object=True, fail_silently=True, fix_protocol=True)
        domain = ".".join([res.subdomain, res.domain])
    except Exception:
        pass

    # 情報量を計算し、スコアを加算
    score += int(round(entropy(domain) * 10))

    # 類似文字を削除する http://www.unicode.org/reports/tr39
    domain = unconfuse(domain)

    words_in_domain = re.split("\W+", domain)

    # 偽の.com .netなどは怪しいのでスコアを上げる (ie. *.com-account-management.info)
    if words_in_domain[0] in ["com", "net", "org"]:
        score += 10

    # suspicious.yamlで定義したキーワードが含まれるドメインのスコアに設定値を加算する
    for word in suspicious["keywords"]:
        if word in domain:
            score += suspicious["keywords"][word]

    # キーワードに設定された値が70以上の疑わしいアイテムが含まれるか確認 (>= 70 points) (ie. paypol)
    for key in [k for (k, s) in suspicious["keywords"].items() if s >= 70]:
        # あまりに一般的なキーワードは除外　(ie. mail.domain.com)
        for word in [w for w in words_in_domain if w not in ["email", "mail", "cloud"]]:
            if distance(str(word), str(key)) == 1:
                score += 70

    # 多くの'-'がふくまれている場合、スコアを加算する (ie. www.paypal-datacenter.com-acccount-alert.com)
    if "xn--" not in domain and domain.count("-") >= 4:
        score += domain.count("-") * 3

    # 深くネストされている場合、スコアを加算する (ie. www.paypal.com.security.accountupdate.gq)
    if domain.count(".") >= 3:
        score += domain.count(".") * 3

    return score

def count_high_score_domains(file_path):
    df = pd.read_csv(file_path, header=None, names=['domain', 'score', 'fingerprint', 'issuer'])
    df['score'] = df['domain'].apply(score_domain)
    count = df[df['score'] >= 150].shape[0]
    return count

yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
file_path = f"/csv/{yesterday}.csv"
count = count_high_score_domains(file_path)
print("The number of domains with score over 150 is:", count)
