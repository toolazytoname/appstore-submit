# 官网三页与自定义域名（Vercel）

App Store 上架最少需要：首页（营销 URL）、隐私政策页（必填）、支持页（技术支持 URL）。静态三页 + Vercel 是最短路径。

## 页面要求

- **隐私政策**：零收集也要写——明确「不收集任何数据」、第三方 SDK 情况、联系方式（邮箱必填，ASC 审核员会看）。
- **支持页**：问题反馈邮箱（mailto）、常见问题可选。
- **首页**：产品名、截图、功能简介、App Store 链接位（上架后补真实链接）。
- 三页部署后逐页 `curl -o /dev/null -w '%{http_code}'` 确认公网 200 再填进 ASC。

## Vercel 部署

```sh
cd site-dir
vercel deploy --prod --yes        # 静态目录直接部署
```

## 自定义域名的大坑（实测）

`vercel alias set <deployment> <domain>` 建的只是**部署级别名**。如果项目开了
`ssoProtection=all_except_custom_domains`（很多模板默认开），alias 域名会被拦到 Vercel 登录页——
curl 看到的是 401/登录跳转，ASC 审核访问也一样被拦。

**正确做法：把域名登记为项目域名**（custom domain 才在 SSO 豁免范围内）：

```sh
# token 与 teamId 来源见 scripts/vercel-add-domain.sh
curl -X POST "https://api.vercel.com/v10/projects/<project>/domains?teamId=<teamId>" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"app.example.com"}'
```

- 登记后确认响应/查询里 `verified: true`，证书会自动签发（Let's Encrypt，几分钟内）。
- DNS：子域名 CNAME 到 `cname.vercel-dns.com`（或按 Vercel 提示）；泛解析已有时直接生效。
- 改完页面内容必须重新 `vercel deploy --prod --yes`，再 curl 验证线上内容已更新。

## bundle id 与域名对应

反向域名惯例：站点 `grove.example.studio` → bundle id `studio.example.grove`。
**ASC 记录的 bundle id 建好后不可换绑**，先在开发者门户注册新 App ID，再建 ASC 记录；
定错只能新建记录重做全部元数据。第一步就和用户把域名、bundle id 一起定死。
