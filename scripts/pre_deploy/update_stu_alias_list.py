import asyncio
import json
import logging

import aiofiles
from cn_sort import sort_text_list

from ..base.const import ALIAS_JSON_PATH, SUFFIX_ALIAS_JSON_PATH
from ..base.utils import async_read_file, replace_brackets, schale_get_stu_data


async def main():
    logging.disable(999)

    cn_stu, jp_stu, en_stu, alias_li, suff_li = await asyncio.gather(
        *[
            schale_get_stu_data("cn"),
            schale_get_stu_data("jp"),
            schale_get_stu_data("en"),
            async_read_file(ALIAS_JSON_PATH),
            async_read_file(SUFFIX_ALIAS_JSON_PATH),
        ]
    )

    # async with aiofiles.open(str(ALIAS_BAK_PATH), "w", encoding="utf-8") as f:
    #     await f.write(alias_li)

    alias_li = json.loads(alias_li)
    suff_li = json.loads(suff_li)

    replaced_alias_li = alias_li

    for s_id, s in cn_stu.items():
        org_li = set(alias_li.get(cn_name := replace_brackets(s["Name"])) or set())

        jp = jp_stu[s_id]
        en = en_stu[s_id]

        jp_n = replace_brackets(jp["Name"])
        en_n = en["Name"].lower()

        if jp_n != cn_name:
            if jp_n in alias_li:
                org_li = set(alias_li[jp_n])
                del alias_li[jp_n]

        org_li.add(jp_n)
        org_li.add(en_n)

        if "(" in cn_name:
            split = cn_name.split("(")
            cn_org_name = split[0]
            suffix = split[1][:-1]
            if ((suffix_alias := suff_li.get(suffix)) is not None) and (
                org_id := [k for k, v in cn_stu.items() if v["Name"] == cn_org_name]
            ):
                org_id = org_id[0]
                org_alias = [cn_org_name] + (alias_li.get(cn_org_name) or [])
                suffix_alias = [suffix] + suffix_alias
                for sa in suffix_alias:
                    for al in org_alias:
                        org_li.add(f"{sa}{al}")

        org_li = list(sort_text_list(list(org_li)))
        replaced_alias_li[cn_name] = org_li
        print(f"stu_alias: {cn_name}: {'; '.join(org_li)}")
        await asyncio.sleep(0)

    async with aiofiles.open(str(ALIAS_JSON_PATH), "w", encoding="utf-8") as f:
        await f.write(
            replace_brackets(
                json.dumps(replaced_alias_li, ensure_ascii=False, indent=2)
            ).lower()
        )

    print("stu_alias: complete")
