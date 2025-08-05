'use client';

import createClient from 'openapi-react-query';
import type { paths } from './api-client';
import { fetchClient } from './api-client-instance';

export const $api = createClient<paths>(fetchClient);
