# Edit a moderation rule

```{warning}
Purging a domain's data removes all objects and caches associated to that domain. This impacts users who have objects from these domains in their libraries.
```

You can change a moderation rule on a domain at any time.

:::{dropdown} Required permissions
:icon: key

- {guilabel}`Moderation` – provides access to the administration and moderation menus.

:::

To update an existing moderation rule:

::::{tab-set}

:::{tab-item} Desktop
:sync: desktop

1. Log in to your {term}`pod`.
2. Select the wrench icon ({fa}`wrench`) at the top of the sidebar to open the {guilabel}`Administration` menu.
3. Select {guilabel}`Moderation`. The {guilabel}`Reports` page opens.
4. Select {guilabel}`Domains` at the top of the page. The {guilabel}`Domains` page opens. You can see a list of known domains on this page.
5. Select the domain with the moderation rule you want to edit. The domain's moderation page opens.
6. Select {guilabel}`Edit` under the {guilabel}`This domain is subject to specific moderation rules` header. The moderation policy form opens.
7. **Optional** – Edit the following settings:
   - {guilabel}`Enabled` – toggle this switch to enable or disable the rule without deleting it.
   - {guilabel}`Reason` – update the reason for the moderation rule.
8. **Optional** – Update your moderation rule:
   - {guilabel}`Block everything` – purge all content from this domain and block all content.
   - {guilabel}`Reject media` – only reject media files such as audio files, avatars, and album art.
9. Select {guilabel}`Update` to save your rule.

:::

:::{tab-item} Mobile
:sync: mobile

1. Log in to your {term}`pod`.
2. Select the wrench icon ({fa}`wrench`) at the top of the screen to open the {guilabel}`Administration` menu.
3. Select {guilabel}`Moderation`. The {guilabel}`Reports` page opens.
4. Select {guilabel}`Domains` at the top of the page. The {guilabel}`Domains` page opens. You can see a list of known domains on this page.
5. Select the domain with the moderation rule you want to edit. The domain's moderation page opens.
6. Select {guilabel}`Edit` under the {guilabel}`This domain is subject to specific moderation rules` header. The moderation policy form opens.
7. **Optional** – Edit the following settings:
   - {guilabel}`Enabled` – toggle this switch to enable or disable the rule without deleting it.
   - {guilabel}`Reason` – update the reason for the moderation rule.
8. **Optional** – Update your moderation rule:
   - {guilabel}`Block everything` – purge all content from this domain and block all content.
   - {guilabel}`Reject media` – only reject media files such as audio files, avatars, and album art.
9. Select {guilabel}`Update` to save your rule.

:::
::::

You're done! The changes to the rule take effect as soon as you update it.
