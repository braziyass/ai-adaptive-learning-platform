import asyncio
import httpx


async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.post('http://127.0.0.1:8000/api/v1/auth/login', json={'email':'admin@example.com','password':'adminpass123'})
        print('LOGIN STATUS', resp.status_code)
        print(resp.text)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            r2 = await client.get('http://127.0.0.1:8000/api/v1/admin/students', headers=headers)
            print('ADMIN STUDENTS', r2.status_code)
            print(r2.text)


if __name__ == '__main__':
    asyncio.run(main())
