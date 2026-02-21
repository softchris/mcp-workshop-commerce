import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import {
  type ClientCapabilitiesWithExtensions,
  UI_EXTENSION_CAPABILITIES,
} from '@mcp-ui/client';

export async function createMcpClient(serverUrl: string): Promise<Client> {
  // Create the client with UI extension capabilities
  const capabilities: ClientCapabilitiesWithExtensions = {
    roots: { listChanged: true },
    extensions: UI_EXTENSION_CAPABILITIES,
  };

  const client = new Client(
    { name: 'my-mcp-client', version: '1.0.0' },
    { capabilities }
  );

  // Connect to the MCP server
  const transport = new StreamableHTTPClientTransport(new URL(serverUrl));
  await client.connect(transport);

  console.log('Connected to MCP server');
  return client;
}