# 1. Title

## 2. Subtitle

Example table

| Head |               Head2               |                Head3 |
| :--- | :-------------------------------: | -------------------: |
| val1 |                 2                 |             **val3** |
|      | ![](https://placehold.co/600x400) | [Google](google.com) |

## 3. Subtitle 2

Examples of text styles:

**bold** text

_italic_ text

<ins>underline</ins> text

**_Bold italic_** text

~~Strike~~ text

==Spoiler== text

---

[Example Link](https://google.com)

[Example Link2][google]

[](https://google.com)

### 3.1. Sub-sub title

Example blocks

> A simple quote block

> A quote block
>
> > Quote in Quote
>
> > <cite>Author</cite>
> >
> > Quote with an author. Only the first `<cite>` tag will be catched. More `<cite>` tags in the same block will be rendered as text.
> >
> > <cite>Author2</cite>
>
> ```python
> Code block in quote
> ```

```js
const example = () => {
  return 1;
};
```

### 3.2. Sub-sub title 2

Example lists

- Item 1
- Item 2
- Item 3

1. Item 1
2. Item 2
3. Item 3

- Item 1
  1. Item-item 1
  2. Item-item 2
- Item 2

1. Item 1
   - Item-item 1
   - Item-item 2
2. Item 2
3. Table in item
   | Test |
   | :---- |
   | This is a table |

#### 3.2.1. H4 title 1

Examples of extensive blocks

> [!caution]
> A caution block is accepted by Typora and GitHub.
>
> It will be rendered as spoiler block in Steam BBcode.

> [!important]
> The important block will be rendered as `[b]...[/b]`.
>
> > [!warning]
> > This is a block in block. it will be rendered as `[u]...[/u]`.

> [!note]
>
> > [!tip]
> >
> > `[!note]` or `[!tip]` blocks will fallback into `[quote]` blocks.

##### 3.2.1.1. H5 title

###### 3.2.1.1.1. H6 title

[google]: https://google.com
