import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Save, Key, Shield, AlertCircle, CheckCircle } from "lucide-react";
import { SUPPORTED_EXCHANGES, getExchangeById } from "@/constants/exchanges";

interface ApiKeyData {
  id?: number;
  exchange: string;
  api_key: string;
  api_secret: string;
  passphrase?: string;
  sandbox_mode: boolean;
  is_active: boolean;
}

interface SettingsPanelProps {
  selectedExchange: string;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ selectedExchange }) => {
  const [apiKeys, setApiKeys] = useState<Record<string, ApiKeyData>>({});
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<
    "idle" | "saving" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        "http://localhost:8000/api/settings/api-keys"
      );
      if (response.ok) {
        const keys = await response.json();
        const keyMap: Record<string, ApiKeyData> = {};
        keys.forEach((key: ApiKeyData) => {
          keyMap[key.exchange] = key;
        });
        setApiKeys(keyMap);
      }
    } catch (error) {
      console.error("Failed to load API keys:", error);
      setErrorMessage("Failed to load API keys");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    exchange: string,
    field: keyof ApiKeyData,
    value: string | boolean
  ) => {
    setApiKeys((prev) => ({
      ...prev,
      [exchange]: {
        ...prev[exchange],
        exchange,
        [field]: value,
        api_key: prev[exchange]?.api_key || "",
        api_secret: prev[exchange]?.api_secret || "",
        sandbox_mode: prev[exchange]?.sandbox_mode || false,
        is_active: prev[exchange]?.is_active !== false,
      },
    }));
  };

  const saveApiKey = async (exchange: string) => {
    const keyData = apiKeys[exchange];
    if (!keyData || !keyData.api_key || !keyData.api_secret) {
      setErrorMessage("API Key and Secret are required");
      setSaveStatus("error");
      return;
    }

    try {
      setSaveStatus("saving");
      setErrorMessage("");

      const response = await fetch(
        "http://localhost:8000/api/settings/api-keys",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(keyData),
        }
      );

      if (response.ok) {
        const savedKey = await response.json();
        setApiKeys((prev) => ({
          ...prev,
          [exchange]: savedKey,
        }));
        setSaveStatus("success");
        setTimeout(() => setSaveStatus("idle"), 2000);
      } else {
        const error = await response.json();
        setErrorMessage(error.detail || "Failed to save API key");
        setSaveStatus("error");
      }
    } catch (error) {
      console.error("Failed to save API key:", error);
      setErrorMessage("Failed to save API key");
      setSaveStatus("error");
    }
  };

  const renderExchangeForm = (exchangeId: string) => {
    const exchangeInfo = getExchangeById(exchangeId);
    if (!exchangeInfo) return null;

    const keyData = apiKeys[exchangeId] || {
      exchange: exchangeId,
      api_key: "",
      api_secret: "",
      passphrase: "",
      sandbox_mode: false,
      is_active: true,
    };

    const isConfigured = keyData.api_key && keyData.api_secret;

    return (
      <Card key={exchangeId} className="w-full">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                {exchangeInfo.displayName} API設定
              </CardTitle>
              <CardDescription>
                {exchangeInfo.displayName}取引所のAPI認証情報を設定してください
              </CardDescription>
            </div>
            {isConfigured && (
              <Badge variant={keyData.is_active ? "default" : "secondary"}>
                {keyData.is_active ? "有効" : "無効"}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              saveApiKey(exchangeId);
            }}
          >
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label htmlFor={`${exchangeId}-api-key`}>API Key</Label>
                <Input
                  id={`${exchangeId}-api-key`}
                  type="text"
                  placeholder="API Keyを入力してください"
                  value={keyData.api_key}
                  onChange={(e) =>
                    handleInputChange(exchangeId, "api_key", e.target.value)
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`${exchangeId}-api-secret`}>API Secret</Label>
                <Input
                  id={`${exchangeId}-api-secret`}
                  type="password"
                  placeholder="API Secretを入力してください"
                  value={keyData.api_secret}
                  onChange={(e) =>
                    handleInputChange(exchangeId, "api_secret", e.target.value)
                  }
                />
              </div>

              {exchangeInfo.hasPassphrase && (
                <div className="space-y-2">
                  <Label htmlFor={`${exchangeId}-passphrase`}>Passphrase</Label>
                  <Input
                    id={`${exchangeId}-passphrase`}
                    type="password"
                    placeholder="Passphraseを入力してください"
                    value={keyData.passphrase || ""}
                    onChange={(e) =>
                      handleInputChange(
                        exchangeId,
                        "passphrase",
                        e.target.value
                      )
                    }
                  />
                </div>
              )}

              {exchangeInfo.hasSandbox && (
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor={`${exchangeId}-sandbox`}>
                      サンドボックスモード
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      テスト環境での取引を有効にします
                    </p>
                  </div>
                  <Switch
                    id={`${exchangeId}-sandbox`}
                    checked={keyData.sandbox_mode}
                    onCheckedChange={(checked) =>
                      handleInputChange(exchangeId, "sandbox_mode", checked)
                    }
                  />
                </div>
              )}

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor={`${exchangeId}-active`}>API有効化</Label>
                  <p className="text-sm text-muted-foreground">
                    このAPIキーを使用可能にします
                  </p>
                </div>
                <Switch
                  id={`${exchangeId}-active`}
                  checked={keyData.is_active}
                  onCheckedChange={(checked) =>
                    handleInputChange(exchangeId, "is_active", checked)
                  }
                />
              </div>
            </div>

            <Separator className="my-4" />

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={loading || saveStatus === "saving"}
                className="flex items-center gap-2"
              >
                {saveStatus === "saving" ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    保存中...
                  </>
                ) : saveStatus === "success" ? (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    保存完了
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    保存
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Shield className="h-6 w-6" />
        <h2 className="text-2xl font-bold">ルート設定</h2>
      </div>

      <p className="text-muted-foreground">
        取引所のAPI認証情報を管理します。APIキーは安全に暗号化されて保存されます。
      </p>

      {errorMessage && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue={SUPPORTED_EXCHANGES[0].id} className="w-full">
        <ScrollArea className="w-full">
          <TabsList className="grid w-full grid-cols-5 lg:grid-cols-8 gap-1">
            {SUPPORTED_EXCHANGES.map((exchange) => (
              <TabsTrigger
                key={exchange.id}
                value={exchange.id}
                className="text-xs"
              >
                {exchange.displayName}
              </TabsTrigger>
            ))}
          </TabsList>
        </ScrollArea>

        {SUPPORTED_EXCHANGES.map((exchange) => (
          <TabsContent key={exchange.id} value={exchange.id} className="mt-6">
            {renderExchangeForm(exchange.id)}
          </TabsContent>
        ))}
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            セキュリティについて
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>• APIキーは暗号化されてローカルデータベースに保存されます</p>
            <p>• 読み取り専用権限のAPIキーの使用を推奨します</p>
            <p>• 定期的にAPIキーを更新することをお勧めします</p>
            <p>
              • サンドボックスモードでテストしてから本番環境で使用してください
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsPanel;
