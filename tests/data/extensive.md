# 1. Extra tests

## 1.1. Test customization

> <cite>Frost</cite>
> Quote with author

| Head 1 | Head 2  |
| :----- | :-----: |
| value1 | value 2 |

## 1.2 Test extensive blocks

> [!caution]
> A caution block is rendered as spoiler block by default.
>
> > [!tag_spoiler]
> > A spoiler block can be specified by `[tag_spoiler]`, too.

> [!important]
> A important block is rendered as bold block by default.
>
> > [!tag_b]
> > A bold block can be specified by `[tag_b]`, too.

> [!warning]
> A warning block is rendered as underline block by default.
>
> > [!tag_u]
> > A warning block can be specified by `[tag_u]`, too.

> [!note]
>
> > [!tip]
> >
> > `[!note]` or `[!tip]` blocks will fallback into `[quote]` blocks.

> [!tag_i]
> An italic block
>
> | Table |
> | :---- |
> | text  |

> [!tag_strike]
> A strike block.
>
> [A link will be marked by `[strike]`, too.](https://google.com)

> [!invalid]
> This is an invalid block, it will fall back into a plain quote block.
