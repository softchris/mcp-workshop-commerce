import { useState, useEffect } from 'react';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { UIResourceRenderer } from '@mcp-ui/client';

interface ToolUIProps {
  client: Client;
  toolName: string;
  toolInput?: Record<string, unknown>;
}

export function ToolUI({ client, toolName, toolInput }: ToolUIProps) {
  const [toolResult, setToolResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [result, setResult] = useState<string>('');
  const [isWaiting, setIsWaiting] = useState(false);

  // Call the tool when input changes
  useEffect(() => {
    if (!toolInput) return;

    setToolResult(null);
    setError(null);

    const callTool = async () => {
      try {
        const result = await client.callTool({
          name: toolName,
          arguments: toolInput,
        });
        setToolResult(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    };

    callTool();
  }, [client, toolName, toolInput]);

  const contentBlocks = toolResult?.content ?? toolResult?.result?.content;
  const resource = contentBlocks?.find((block: any) => block?.type === 'resource')?.resource;

  if (error) {
    return <div style={{ color: 'red' }}>Error: {error}</div>;
  }

  if (!toolResult) {
    return <div style={{ padding: '12px' }}>Running tool...</div>;
  }

  if (!resource) {
    return (
      <div style={{ color: 'red' }}>
        Error: Tool {toolName} returned no UI resource.
        <pre style={{ whiteSpace: 'pre-wrap', marginTop: '12px', color: '#444' }}>
          {JSON.stringify(toolResult, null, 2)}
        </pre>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666' }}>
        UI debug: {resource?.uri} ({resource?.mimeType})
      </div>
      <UIResourceRenderer
        resource={resource}
        htmlProps={{
          sandboxPermissions: 'allow-same-origin allow-scripts allow-forms allow-popups',
          autoResizeIframe: { height: true },
          style: { width: '100%', height: '200px', border: 'none' },
        }}
        onUIAction={async (result) => {
          console.log('UI action:', result);

         const { type } = result; 
         if (type === 'tool') {
            const { toolName: tn } = result.payload;

            setIsWaiting(true);
            try {
              const toolResult = await client.callTool({
                name: tn,
                arguments: result.payload.params,
              });

              const blocks = Array.isArray(toolResult?.content) ? toolResult.content : [];
              const parsedResult = blocks[0]?.text ?? '';

              console.log('Result from tool called by UI action:', parsedResult);
              // alert(`Result: ${parsedResult}`);
              setResult(parsedResult);
            } finally {
              setIsWaiting(false);
            }
         }

          

          return { isError: false } as any;
        }}
      />
      {isWaiting ? (
        <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
          Waiting for tool response...
        </div>
      ) : null}
      <div style={{ marginTop: '8px', fontSize: '14px', color: '#333', border: 'solid 1px grey', padding: '8px', borderRadius: '4px' }}>
        <h2>Tool result: </h2> {result}
      </div>
      <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
        Raw resource text preview:
      </div>

    </div>
  );
}