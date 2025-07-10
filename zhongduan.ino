//引入头文件
#include "DHT.h"
#include "TM1637Display.h"
#include <WiFiS3.h> 
c:\Users\tangx\Desktop\zhongduan\zhongduan.ino
//定义引脚
#define DHTPIN 2
#define LED_1 12         
#define LED_2 13
#define CLK 4
#define DIO 3

//定义使用的传感器类型
#define DHTTYPE DHT11

//初始化对象
TM1637Display display(CLK, DIO);
DHT dht(DHTPIN, DHTTYPE);
const char* ssid = "XXXX";  
const char* password = "XXXX";  
const char* serverIP = "XXXX"; 
const int serverPort = XXXX;  

WiFiClient client; 

void setup() {
  Serial.begin(9600);

  pinMode(LED_1,OUTPUT);
  pinMode(LED_2,OUTPUT);

  dht.begin();
  display.setBrightness(0x0f); 

  //连接WiFi
  WiFi.begin(ssid, password);  
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    for(int i=0;i<10;i++){
      digitalWrite(LED_1,1);
      delay(50);
      digitalWrite(LED_1,0);
    }
  } 
  Serial.println("WiFi已连接");
  digitalWrite(LED_1,1);
    
  Serial.println(WiFi.localIP());

  //连接服务器
  while(!client.connect(serverIP, serverPort)){
    Serial.println("连接中...");
    for(int i=0;i<10;i++){
      digitalWrite(LED_2,1);
      delay(50);
      digitalWrite(LED_2,0);
    }
  }
  
  if (client.connect(serverIP, serverPort)) {  
    Serial.println("已连接到龙芯教育派");
    digitalWrite(LED_2,1);
  } else {  
    Serial.println("连接失败"); 
    digitalWrite(LED_2,0); 
  }  
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  //处理数据
  int tempInt = (int)temperature;
  int tempDec = (int)(temperature * 10) % 10; 
  display.showNumberDecEx(tempInt * 10 + tempDec, 0b1000, false, 4, 0); 
  delay(2000);
  display.showNumberDec((uint16_t)humidity, false, 2, 0);  

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" °C, Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  //连接服务器
  if (!client.connected()) {
    Serial.println("尝试连接到服务器...");
    digitalWrite(LED_2,0);
  }
  if (client.connect(serverIP, serverPort)) {
    Serial.println("已连接到服务器");
    digitalWrite(LED_2,1);

  }

  char str[50];
  sprintf(str,"%s,%.2f,%.2f","device002",temperature,humidity);
  client.println(str);
  Serial.println(str);

  delay(300000);

}
