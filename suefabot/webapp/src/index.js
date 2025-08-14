import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

Sentry.init({
	dsn: process.env.REACT_APP_SENTRY_DSN || '',
	integrations: [new BrowserTracing()],
	tracesSampleRate: 0.2,
	environment: process.env.NODE_ENV || 'development',
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
	<React.StrictMode>
		<Sentry.ErrorBoundary fallback={<div>Something went wrong.</div>}>
			<App />
		</Sentry.ErrorBoundary>
	</React.StrictMode>
);