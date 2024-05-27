since api only works for your account?
```javascript
[...document.querySelectorAll("#__layout > div > main > div > div > div.relative.min-w-0.grow > div > div:nth-child(5) > div > div:nth-child(2) > ul > div.mb-2.mt-2 > div > div > div > div.w-full.overflow-hidden > div.-mt-0\\.5.ellipsis > a")]
.map((e) => e.href.match(/\d+/g)[0])
.map((s) => `https://samedia-b2-west.b-cdn.net/com-sermonaudio-sermons/${s}.mp3`)
.join("\n")
```
