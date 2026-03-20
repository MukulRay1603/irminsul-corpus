<!-- Source: KQM Theorycrafting Library — docs\characters\README.md -->
<!-- License: https://github.com/KQM-git/TCL/blob/master/LICENSE -->

---
sidebar_position: 2001
---

# Characters

Characters are organized per Element.

## Elements

import DocCardList from '@theme/DocCardList';

<DocCardList />

## All Characters

import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={
    useCurrentSidebarCategory().items
        .flatMap(i => i.type == "category" ? i.items : [])
        .sort((a, b) => a.label.localeCompare(b.label))
}/> 
