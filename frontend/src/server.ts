import 'zone.js/node';

import { APP_BASE_HREF } from '@angular/common';
import { CommonEngine } from '@angular/ssr/node';
import * as express from 'express';
import { Request, Response, NextFunction } from 'express';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { bootstrap } from './main.server';

export function app(): express.Express {
    const server = express();
    const distFolder = join(process.cwd(), 'dist/crialt-frontend/browser');
    const indexHtml = existsSync(join(distFolder, 'index.original.html'))
        ? 'index.original.html'
        : 'index.html';

    const commonEngine = new CommonEngine();

    server.disable('x-powered-by');
    server.use((req: Request, res: Response, next: NextFunction) => {
        res.setHeader('X-Content-Type-Options', 'nosniff');
        res.setHeader('X-Frame-Options', 'SAMEORIGIN');
        res.setHeader('X-XSS-Protection', '1; mode=block');
        next();
    });

    server.set('view engine', 'html');
    server.set('views', distFolder);

    server.get('*.*', express.static(distFolder, { maxAge: '1y' }));

    server.get('*', (req: Request, res: Response) => {
        const { protocol, originalUrl, headers } = req;
        const baseHref = req.baseUrl || '/';
        commonEngine
            .render({
                bootstrap,
                documentFilePath: join(distFolder, indexHtml),
                url: `${protocol}://${headers.host}${originalUrl}`,
                publicPath: distFolder,
                providers: [{ provide: APP_BASE_HREF, useValue: baseHref }],
            })
            .then((html) => res.status(200).send(html))
            .catch((err) => {
                console.error(err);
                res.status(500).send(err.message);
            });
    });

    return server;
}

function run(): void {
    const port = process.env['PORT'] || 4000;
    const server = app();
    server.listen(port, () => {
        console.log(`Node Express server listening on http://localhost:${port}`);
    });
}

run();

export default bootstrap;
