# DirectLine和CSP修复说明

## 问题概述

在部署过程中，我们遇到了两个主要问题：

1. **DirectLine令牌生成错误**：
   ```
   "error": "Failed to generate token: {
     "error": {
       "code": "BadArgument",
       "message": "User id must start with \"dl_\"."
     }
   }"
   ```

2. **内容安全策略(CSP)阻止JavaScript评估**：
   ```
   Content Security Policy of your site blocks the use of 'eval' in JavaScript
   ```

## 修复方案

### 1. DirectLine用户ID格式修复

DirectLine要求用户ID必须以`dl_`开头，但我们之前使用了`dl-user-`前缀。修复步骤：

1. 在`app/api/direct_line_proxy.py`中，修改`generate_token`函数：
   ```python
   # 修改前
   user_id = request.json.get('user_id', f'dl-user-{int(time.time())}')
   
   # 修改后
   user_id = request.json.get('user_id', f'dl_{int(time.time())}')
   ```

2. 在`app/static/index.html`中，修改前端用户ID生成：
   ```javascript
   // 修改前
   const userId = 'dl-user-' + Date.now().toString();
   
   // 修改后
   const userId = 'dl_' + Date.now().toString();
   ```

### 2. 内容安全策略(CSP)修复

WebChat组件需要使用JavaScript评估功能，需要在CSP中添加`unsafe-eval`：

```html
<!-- 修改前 -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self' https://*.botframework.com; connect-src 'self' https://*.botframework.com wss://*.botframework.com https://*.azure.com; script-src 'self' https://cdn.botframework.com 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' https://*.botframework.com data:;">

<!-- 修改后 -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self' https://*.botframework.com; connect-src 'self' https://*.botframework.com wss://*.botframework.com https://*.azure.com; script-src 'self' https://cdn.botframework.com 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' https://*.botframework.com data:;">
```

## 验证方法

1. 使用测试脚本验证DirectLine令牌生成：
   ```bash
   python test_directline_fix.py --url https://你的应用URL --secret 你的DirectLine密钥
   ```

2. 通过浏览器访问应用，检查控制台是否有CSP或DirectLine相关错误。

## 安全考虑

1. `unsafe-eval`会降低安全性，但对于WebChat组件是必需的。长期解决方案可以考虑使用自定义WebChat客户端，避免使用eval。

2. DirectLine令牌应该仅在需要时生成，并合理设置过期时间。

## 注意事项

如果在修复后仍遇到问题，请检查：

1. 应用重启后的日志，确认修改已生效
2. Bot Service的DirectLine通道配置是否正确
3. 网络环境是否正常，可能存在防火墙阻止 